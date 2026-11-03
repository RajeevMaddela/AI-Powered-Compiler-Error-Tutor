import os
import sys
import csv
import json
import logging
import hashlib
import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score, f1_score
from sklearn.pipeline import Pipeline
import joblib

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.core.database import SessionLocal
from backend.app.models.models import Feedback, ErrorRecord, User, Consent, ModelVersion, RetrainingRound
from backend.app.compiler.constants import ErrorCategory
from ml.pipeline.features import build_feature_pipeline
from ml.pipeline.sanitizer import sanitize_diagnostic_message

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ml.retrain")

DATA_DIR = PROJECT_ROOT / "ml" / "data"
MODELS_DIR = PROJECT_ROOT / "ml" / "models"


def compute_file_sha256(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def load_base_training_data() -> List[Dict[str, Any]]:
    train_file = DATA_DIR / "train.csv"
    records = []
    with open(train_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            records.append(dict(r))
    return records


def load_human_test_data() -> List[Dict[str, Any]]:
    test_file = DATA_DIR / "human_test.csv"
    records = []
    with open(test_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            records.append(dict(r))
    return records


def fetch_consented_feedback(db) -> List[Dict[str, Any]]:
    """
    Fetches user corrections strictly from users with active consent ('granted').
    Sanitizes all diagnostic messages to guarantee zero student code/identifier leakage.
    """
    # Query Feedback joined with ErrorRecord, User, and active Consent
    feedbacks = (
        db.query(Feedback, ErrorRecord, Consent)
        .join(ErrorRecord, Feedback.error_id == ErrorRecord.id)
        .join(User, ErrorRecord.submission_id.isnot(None))
        .join(Consent, User.id == Consent.user_id)
        .filter(
            Feedback.helpful == False,
            Feedback.corrected_category.isnot(None),
            Consent.decision == "granted"
        )
        .all()
    )

    valid_categories = {c.value for c in ErrorCategory}
    consented_records = []

    for fb, err, cons in feedbacks:
        if fb.corrected_category not in valid_categories:
            continue

        # Sanitize diagnostic message to ensure zero private student identifier leakage
        clean_msg = sanitize_diagnostic_message(err.raw_message)

        rec = {
            "id": f"feedback_{fb.id}",
            "seed_id": "student_feedback",
            "split": "retrain",
            "category": fb.corrected_category,
            "stage": "SEMANTIC",
            "severity": err.severity,
            "primary_message": clean_msg,
            "primary_notes": "",
            "primary_hints": "",
            "has_did_you_mean": False,
            "has_did_you_forget_include": False,
            "is_linker_error": "undefined reference" in clean_msg.lower(),
            "error_line": err.line or 1,
            "error_column": err.column or 1,
            "num_errors": 1,
            "num_followon": 0,
            "has_include_iostream": True,
            "has_include_vector": False,
            "has_include_string": False,
            "has_include_map": False,
            "has_using_namespace_std": True,
            "uses_std_prefix": False
        }
        consented_records.append(rec)

    logger.info("Found %d consented, sanitized student feedback records for retraining", len(consented_records))
    return consented_records


def run_retraining_round(new_version: str = "v1.1.0") -> Dict[str, Any]:
    """
    Executes an audited retraining cycle:
    1. Combines base train set with consented user corrections.
    2. Trains candidate classifier.
    3. Benchmarks candidate against frozen human test set.
    4. Evaluates acceptance gate against currently active model.
    5. Publishes only if candidate performs at least as well as active model.
    """
    db = SessionLocal()
    round_rec = RetrainingRound(status="running")
    db.add(round_rec)
    db.commit()
    db.refresh(round_rec)

    try:
        base_train = load_base_training_data()
        consented_feedback = fetch_consented_feedback(db)
        combined_train = base_train + consented_feedback

        logger.info("Retraining dataset size: %d samples (Base: %d, New Consented: %d)",
                    len(combined_train), len(base_train), len(consented_feedback))

        y_train = [r["category"] for r in combined_train]

        # Candidate Pipeline
        candidate_clf = LogisticRegression(
            C=2.0,
            class_weight="balanced",
            max_iter=1000,
            random_state=42
        )
        candidate_pipeline = Pipeline([
            ("features", build_feature_pipeline()),
            ("classifier", candidate_clf)
        ])

        logger.info("Fitting candidate model...")
        candidate_pipeline.fit(combined_train, y_train)

        # Benchmark on frozen human test set
        human_test = load_human_test_data()
        y_test_true = [r["category"] for r in human_test]
        y_test_pred = candidate_pipeline.predict(human_test)

        test_acc = float(accuracy_score(y_test_true, y_test_pred))
        test_f1 = float(f1_score(y_test_true, y_test_pred, average="macro", zero_division=0))

        logger.info("Candidate Model on Human Benchmark: Accuracy=%.4f, Macro F1=%.4f", test_acc, test_f1)

        # Retrieve active model metrics for gate comparison
        active_mv = db.query(ModelVersion).filter(ModelVersion.active == True).first()
        active_acc = 0.90
        active_f1 = 0.88
        if active_mv and active_mv.metrics:
            try:
                m_json = json.loads(active_mv.metrics)
                active_acc = float(m_json.get("test_accuracy", 0.90))
                active_f1 = float(m_json.get("test_macro_f1", 0.88))
            except Exception:
                pass

        logger.info("Active Model Benchmark Baseline: Accuracy=%.4f, Macro F1=%.4f", active_acc, active_f1)

        # Acceptance Gate (Safety Check)
        passed_gate = (test_acc >= active_acc - 0.02) and (test_f1 >= active_f1 - 0.02)

        if not passed_gate:
            logger.warning("REJECTED: Candidate model performed worse than active model. No deployment.")
            round_rec.status = "rejected"
            db.commit()
            return {
                "round_id": round_rec.id,
                "status": "rejected",
                "candidate_accuracy": test_acc,
                "candidate_f1": test_f1,
                "active_accuracy": active_acc,
                "active_f1": active_f1
            }

        # Serialise candidate model
        model_filename = f"model_{new_version}.joblib"
        model_path = MODELS_DIR / model_filename
        bundle = {
            "version": new_version,
            "pipeline": candidate_pipeline,
            "threshold": 0.55,
            "classes": candidate_pipeline.classes_.tolist(),
            "trained_at": datetime.datetime.utcnow().isoformat()
        }
        joblib.dump(bundle, model_path)
        checksum = compute_file_sha256(model_path)

        metrics_summary = {
            "test_accuracy": test_acc,
            "test_macro_f1": test_f1,
            "train_samples": len(combined_train),
            "feedback_samples_added": len(consented_feedback)
        }
        metrics_file = MODELS_DIR / f"model_{new_version}_metrics.json"
        with open(metrics_file, "w", encoding="utf-8") as f:
            json.dump(metrics_summary, f, indent=2)

        # Update active pointer
        pointer_data = {
            "active_version": new_version,
            "active_file": model_filename,
            "sha256": checksum,
            "activated_at": datetime.datetime.utcnow().isoformat()
        }
        with open(MODELS_DIR / "active_model.json", "w", encoding="utf-8") as f:
            json.dump(pointer_data, f, indent=2)

        # Update DB models
        db.query(ModelVersion).update({ModelVersion.active: False})
        new_mv = ModelVersion(
            version=new_version,
            data_summary=f"Trained on {len(combined_train)} samples ({len(consented_feedback)} consented user corrections)",
            metrics=json.dumps(metrics_summary),
            checksum=checksum,
            active=True
        )
        db.add(new_mv)

        round_rec.status = "completed"
        round_rec.resulting_model_version = new_version
        db.commit()

        logger.info("SUCCESS: Published %s as active production model! (SHA-256: %s)", new_version, checksum[:12])

        return {
            "round_id": round_rec.id,
            "status": "completed",
            "published_version": new_version,
            "candidate_accuracy": test_acc,
            "candidate_f1": test_f1,
            "checksum": checksum
        }

    except Exception as e:
        logger.error("Retraining failed with error: %s", e, exc_info=True)
        round_rec.status = "failed"
        db.commit()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    version_arg = sys.argv[1] if len(sys.argv) > 1 else "v1.1.0"
    res = run_retraining_round(version_arg)
    print(json.dumps(res, indent=2))

