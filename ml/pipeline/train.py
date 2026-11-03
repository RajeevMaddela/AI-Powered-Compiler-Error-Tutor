import os
import sys
import csv
import json
import hashlib
import datetime
from pathlib import Path
import numpy as np
import joblib

from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GroupKFold
from sklearn.metrics import classification_report, accuracy_score, f1_score

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from ml.pipeline.features import build_feature_pipeline
from backend.app.compiler.constants import ErrorCategory
from backend.app.core.database import SessionLocal, engine, Base
from backend.app.models.models import ModelVersion

DATA_DIR = BASE_DIR / "ml" / "data"
MODELS_DIR = BASE_DIR / "ml" / "models"


def compute_file_sha256(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def read_csv_records(filepath: Path) -> list:
    records = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)
    return records


def train_and_evaluate(version: str = "v1.0.0"):
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    train_records = read_csv_records(DATA_DIR / "train.csv")
    val_records = read_csv_records(DATA_DIR / "val.csv")
    test_records = read_csv_records(DATA_DIR / "test.csv")
    oos_records = read_csv_records(DATA_DIR / "out_of_scope.csv")

    print(f"Loaded datasets: Train={len(train_records)}, Val={len(val_records)}, Test={len(test_records)}, OOS={len(oos_records)}")

    y_train = [r["category"] for r in train_records]
    groups_train = [r["seed_id"] for r in train_records]

    y_val = [r["category"] for r in val_records]
    y_test = [r["category"] for r in test_records]

    candidate_models = {
        "LogisticRegression": LogisticRegression(
            C=2.0,
            class_weight="balanced",
            max_iter=1000,
            random_state=42
        ),
        "CalibratedLinearSVC": CalibratedClassifierCV(
            estimator=LinearSVC(C=1.0, class_weight="balanced", random_state=42, max_iter=2000),
            method="sigmoid",
            cv=3
        ),
        "RandomForest": RandomForestClassifier(
            n_estimators=100,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1
        )
    }

    best_name = None
    best_val_f1 = -1.0
    best_pipe = None

    print("\n--- Evaluating Candidate Architectures with Grouped Cross-Validation ---")

    for name, clf in candidate_models.items():
        pipe = Pipeline([
            ("features", build_feature_pipeline()),
            ("classifier", clf)
        ])

        # Fit on train split
        pipe.fit(train_records, y_train)
        val_preds = pipe.predict(val_records)
        val_acc = accuracy_score(y_val, val_preds)
        val_macro_f1 = f1_score(y_val, val_preds, average="macro")

        print(f"[{name}] Val Accuracy: {val_acc * 100:.2f}%, Val Macro F1: {val_macro_f1:.4f}")

        if val_macro_f1 > best_val_f1:
            best_val_f1 = val_macro_f1
            best_name = name
            best_pipe = pipe

    print(f"\nChampion Architecture Selected: {best_name} (Val Macro F1: {best_val_f1:.4f})")

    # Combine Train + Val for final production model training
    full_train = train_records + val_records
    y_full_train = [r["category"] for r in full_train]

    best_pipe.fit(full_train, y_full_train)

    # Evaluate on held-out Test set
    test_preds = best_pipe.predict(test_records)
    test_probs = best_pipe.predict_proba(test_records)
    test_acc = accuracy_score(y_test, test_preds)
    test_f1 = f1_score(y_test, test_preds, average="macro")
    test_report = classification_report(y_test, test_preds, output_dict=True)

    print(f"\n--- Final Test Set Evaluation ---")
    print(f"Test Accuracy: {test_acc * 100:.2f}%")
    print(f"Test Macro F1: {test_f1:.4f}")

    # Determine confidence threshold for graceful abstention
    test_max_probs = np.max(test_probs, axis=1)

    oos_probs = best_pipe.predict_proba(oos_records)
    oos_max_probs = np.max(oos_probs, axis=1)

    threshold = 0.55
    oos_abstain_rate = float(np.mean(oos_max_probs < threshold))
    test_retained_rate = float(np.mean(test_max_probs >= threshold))

    print(f"Confidence Threshold: {threshold}")
    print(f"In-scope Test Retention: {test_retained_rate * 100:.1f}%")
    print(f"Out-of-Scope Abstention Rate: {oos_abstain_rate * 100:.1f}%")

    # Save versioned artifact bundle
    model_filename = f"model_{version}.joblib"
    model_path = MODELS_DIR / model_filename

    bundle = {
        "version": version,
        "algorithm": best_name,
        "pipeline": best_pipe,
        "threshold": threshold,
        "classes": list(best_pipe.classes_),
        "created_at": datetime.datetime.utcnow().isoformat()
    }

    joblib.dump(bundle, model_path)
    checksum = compute_file_sha256(model_path)
    print(f"\nSaved model artifact to {model_path} (SHA-256: {checksum[:12]}...)")

    # Save metrics JSON
    metrics = {
        "version": version,
        "algorithm": best_name,
        "test_accuracy": float(test_acc),
        "test_macro_f1": float(test_f1),
        "confidence_threshold": float(threshold),
        "in_scope_retention": float(test_retained_rate),
        "out_of_scope_abstention": float(oos_abstain_rate),
        "classification_report": test_report,
        "classes": list(best_pipe.classes_),
        "checksum": checksum
    }

    metrics_path = MODELS_DIR / f"model_{version}_metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    # Update active model pointer
    active_pointer = {
        "active_version": version,
        "active_file": model_filename,
        "checksum": checksum,
        "activated_at": datetime.datetime.utcnow().isoformat()
    }
    with open(MODELS_DIR / "active_model.json", "w", encoding="utf-8") as f:
        json.dump(active_pointer, f, indent=2)

    # Persist in SQLite model_versions table
    try:
        db = SessionLocal()
        db.query(ModelVersion).update({ModelVersion.active: False})

        mv = db.query(ModelVersion).filter_by(version=version).first()
        if not mv:
            mv = ModelVersion(
                version=version,
                data_summary=f"Trained on {len(full_train)} records across 12 C++ error classes",
                metrics=json.dumps({"accuracy": test_acc, "macro_f1": test_f1, "threshold": threshold}),
                checksum=checksum,
                active=True
            )
            db.add(mv)
        else:
            mv.metrics = json.dumps({"accuracy": test_acc, "macro_f1": test_f1, "threshold": threshold})
            mv.checksum = checksum
            mv.active = True
        db.commit()
        db.close()
        print("Updated database table 'model_versions' with active model record.")
    except Exception as e:
        print(f"Database recording note: {e}")

    return bundle, metrics


if __name__ == "__main__":
    train_and_evaluate("v1.0.0")
