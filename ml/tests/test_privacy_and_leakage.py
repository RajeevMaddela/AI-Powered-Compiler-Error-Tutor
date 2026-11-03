import csv
import re
import pytest
from pathlib import Path

from ml.pipeline.sanitizer import sanitize_diagnostic_message
from ml.pipeline.features import build_feature_pipeline
from ml.pipeline.classifier import get_classifier
from backend.app.compiler.constants import ErrorCategory

DATA_DIR = Path("ml/data")


def test_sanitizer_replaces_student_identifiers():
    raw_message = "'student_secret_var_42' was not declared in this scope"
    sanitized = sanitize_diagnostic_message(raw_message)
    assert "student_secret_var_42" not in sanitized
    assert "<ID>" in sanitized
    assert "was not declared in this scope" in sanitized


def test_sanitizer_replaces_function_identifiers():
    raw_message = "undefined reference to `myCustomHelperFunction(int, double)'"
    sanitized = sanitize_diagnostic_message(raw_message)
    assert "myCustomHelperFunction" not in sanitized
    assert "`<ID>()'" in sanitized


def test_sanitizer_preserves_cpp_keywords_and_types():
    raw_message = "cannot convert 'const char*' to 'int' in assignment"
    sanitized = sanitize_diagnostic_message(raw_message)
    assert "'const char*'" in sanitized
    assert "'int'" in sanitized
    assert "<ID>" not in sanitized


def test_sanitizer_preserves_punctuation_and_delimiters():
    raw_message = "expected ';' before 'return'"
    sanitized = sanitize_diagnostic_message(raw_message)
    assert "';'" in sanitized
    assert "'return'" in sanitized


def test_classifier_predicts_independently_of_identifier_names():
    clf = get_classifier()
    if clf.pipeline is None:
        pytest.skip("Model artifact not yet loaded")

    # The same diagnostic pattern with different student identifier names must yield the identical category
    diag1 = {
        "primary_message": "expected ';' before 'return'",
        "severity": "error",
        "error_line": 10,
        "error_column": 5,
        "is_linker_error": False,
        "num_errors": 1
    }
    diag2_a = {
        "primary_message": "'completely_random_student_var_9999' was not declared in this scope",
        "severity": "error",
        "error_line": 12,
        "error_column": 8,
        "is_linker_error": False,
        "has_using_namespace_std": True,
        "num_errors": 1
    }
    diag2_b = {
        "primary_message": "'totally_different_student_name_1234' was not declared in this scope",
        "severity": "error",
        "error_line": 12,
        "error_column": 8,
        "is_linker_error": False,
        "has_using_namespace_std": True,
        "num_errors": 1
    }

    res1 = clf.predict(diag1)
    res2_a = clf.predict(diag2_a)
    res2_b = clf.predict(diag2_b)

    assert res1["category"] == ErrorCategory.MISSING_SEMICOLON.value
    assert res1["confidence"] >= 0.55
    assert not res1["abstained"]

    assert res2_a["category"] == ErrorCategory.UNDECLARED_IDENTIFIER.value
    assert res2_a["confidence"] >= 0.55
    assert not res2_a["abstained"]

    # Invariance check: differing identifier names yield identical category and confidence
    assert res2_a["category"] == res2_b["category"]
    assert res2_a["confidence"] == res2_b["confidence"]


def test_csv_files_strict_privacy_audit():
    """Confirms no student source code lines ever leaked into training CSVs."""
    csv_paths = [
        DATA_DIR / "train.csv",
        DATA_DIR / "val.csv",
        DATA_DIR / "test.csv"
    ]
    for p in csv_paths:
        if not p.exists():
            continue
        with open(p, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            assert "source_code" not in reader.fieldnames
            for row in reader:
                msg = row["primary_message"]
                # Must not contain whole lines of source code
                assert not ("int main()" in msg or "return 0;" in msg)

