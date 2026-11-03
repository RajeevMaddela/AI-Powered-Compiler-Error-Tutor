import os
import json
import csv
import pytest
from pathlib import Path
from backend.app.compiler.constants import ErrorCategory

DATA_DIR = Path("ml/data")
DATASET_JSONL = DATA_DIR / "dataset.jsonl"
HUMAN_JSONL = DATA_DIR / "human_test.jsonl"
OOS_JSONL = DATA_DIR / "out_of_scope.jsonl"

def test_jsonl_schema_validation():
    if not DATASET_JSONL.exists():
        pytest.skip("dataset.jsonl not yet generated")

    valid_cats = {c.value for c in ErrorCategory}
    valid_splits = {"train", "val", "test"}

    required_keys = {
        "id", "dataset_version", "source_type", "seed_id", "split",
        "category", "stage", "mutator", "mutation", "source_code",
        "source_sha256", "compiler", "exit_code", "raw_output",
        "primary", "is_linker_error", "num_diagnostics", "num_errors",
        "num_followon", "stdlib_flags", "verification"
    }

    with open(DATASET_JSONL, "r", encoding="utf-8") as f:
        count = 0
        for line in f:
            rec = json.loads(line)
            assert required_keys.issubset(rec.keys())
            assert rec["category"] in valid_cats
            assert rec["split"] in valid_splits
            assert isinstance(rec["primary"], dict)
            assert "message" in rec["primary"]
            count += 1
        assert count > 0

def test_grouped_split_leakage():
    """Ensure no seed_id appears in more than one split (train/val/test)"""
    if not DATASET_JSONL.exists():
        pytest.skip("dataset.jsonl not yet generated")

    seed_splits = {}
    with open(DATASET_JSONL, "r", encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            sid = rec["seed_id"]
            sp = rec["split"]
            if sid in seed_splits:
                assert seed_splits[sid] == sp, f"Leakage: Seed {sid} found in both {seed_splits[sid]} and {sp}"
            else:
                seed_splits[sid] = sp

def test_human_test_isolation():
    """Ensure no human test or out-of-scope program source appears in the training dataset"""
    if not DATASET_JSONL.exists() or not HUMAN_JSONL.exists() or not OOS_JSONL.exists():
        pytest.skip("Datasets not yet generated")

    dataset_hashes = set()
    with open(DATASET_JSONL, "r", encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            dataset_hashes.add(rec["source_sha256"])

    with open(HUMAN_JSONL, "r", encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            assert rec["source_sha256"] not in dataset_hashes, "Leakage: Human test file found in main dataset!"

    with open(OOS_JSONL, "r", encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            assert rec["source_sha256"] not in dataset_hashes, "Leakage: Out-of-scope file found in main dataset!"

def test_csv_privacy():
    """Model-facing CSV files must NOT contain any source code or source lines"""
    csv_files = [
        DATA_DIR / "train.csv",
        DATA_DIR / "val.csv",
        DATA_DIR / "test.csv",
        DATA_DIR / "human_test.csv",
        DATA_DIR / "out_of_scope.csv"
    ]

    for cpath in csv_files:
        if not cpath.exists():
            continue
        with open(cpath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []
            assert "source_code" not in fieldnames
            assert "source_line" not in fieldnames
            assert "code" not in fieldnames
            for row in reader:
                # Primary message should not be full source code
                msg = row["primary_message"]
                assert not ("#include" in msg and "int main" in msg)
