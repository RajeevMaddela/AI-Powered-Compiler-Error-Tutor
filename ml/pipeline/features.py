import csv
import numpy as np
import scipy.sparse as sp
from typing import Dict, Any, List, Union
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion, Pipeline

from ml.pipeline.sanitizer import sanitize_diagnostic_message


class DiagnosticTextExtractor(BaseEstimator, TransformerMixin):
    """
    Extracts and sanitizes primary message, notes, and hints into a single normalized text string.
    Works with both lists of dicts (from CSV/JSON/API) and plain message strings.
    """
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        combined = []
        for item in X:
            if isinstance(item, dict):
                m = str(item.get("primary_message") or item.get("message") or "")
                n = str(item.get("primary_notes") or item.get("notes") or "")
                h = str(item.get("primary_hints") or item.get("hints") or "")
            else:
                m = str(item or "")
                n = ""
                h = ""

            san_m = sanitize_diagnostic_message(m)
            san_n = sanitize_diagnostic_message(n)
            san_h = sanitize_diagnostic_message(h)
            combined.append(f"{san_m} {san_n} {san_h}".strip())
        return combined


class DomainFeatureExtractor(BaseEstimator, TransformerMixin):
    """
    Extracts tabular domain flags and numeric metadata.
    """
    BOOL_COLS = [
        "has_did_you_mean",
        "has_did_you_forget_include",
        "is_linker_error",
        "has_include_iostream",
        "has_include_vector",
        "has_include_string",
        "has_include_map",
        "has_using_namespace_std",
        "uses_std_prefix",
    ]

    def fit(self, X, y=None):
        return self

    def _to_bool(self, val: Any) -> float:
        if isinstance(val, bool):
            return 1.0 if val else 0.0
        if isinstance(val, (int, float)):
            return 1.0 if val > 0 else 0.0
        if isinstance(val, str):
            return 1.0 if val.strip().lower() in ("true", "1", "yes") else 0.0
        return 0.0

    def _to_num(self, val: Any) -> float:
        try:
            if val is None or val == "":
                return 0.0
            return float(val)
        except (ValueError, TypeError):
            return 0.0

    def transform(self, X):
        n = len(X)
        feature_cols = []

        # 1. Boolean flags
        for col in self.BOOL_COLS:
            col_vals = [self._to_bool(item.get(col, False) if isinstance(item, dict) else False) for item in X]
            feature_cols.append(np.array(col_vals, dtype=np.float64).reshape(-1, 1))

        # 2. Severity encoding (error, warning, fatal error)
        sev_error = []
        sev_warning = []
        sev_fatal = []
        for item in X:
            sev = str(item.get("severity", "error") if isinstance(item, dict) else "error").lower()
            sev_error.append(1.0 if sev == "error" else 0.0)
            sev_warning.append(1.0 if sev == "warning" else 0.0)
            sev_fatal.append(1.0 if "fatal" in sev else 0.0)

        feature_cols.append(np.array(sev_error, dtype=np.float64).reshape(-1, 1))
        feature_cols.append(np.array(sev_warning, dtype=np.float64).reshape(-1, 1))
        feature_cols.append(np.array(sev_fatal, dtype=np.float64).reshape(-1, 1))

        # 3. Numeric log1p counts: num_errors, num_followon, error_line, error_column
        for col in ["num_errors", "num_followon", "error_line", "error_column"]:
            nums = [np.log1p(max(0.0, self._to_num(item.get(col, 0) if isinstance(item, dict) else 0))) for item in X]
            feature_cols.append(np.array(nums, dtype=np.float64).reshape(-1, 1))

        dense_mat = np.hstack(feature_cols)
        return sp.csr_matrix(dense_mat)


def build_feature_pipeline() -> FeatureUnion:
    """
    Builds composite feature union combining Word TF-IDF, Char TF-IDF,
    and structured domain features.
    """
    word_vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=2,
        max_features=2500,
        sublinear_tf=True
    )

    char_vectorizer = TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(3, 5),
        min_df=2,
        max_features=2500,
        sublinear_tf=True
    )

    text_word_pipe = Pipeline([
        ("extract", DiagnosticTextExtractor()),
        ("tfidf_word", word_vectorizer)
    ])

    text_char_pipe = Pipeline([
        ("extract", DiagnosticTextExtractor()),
        ("tfidf_char", char_vectorizer)
    ])

    union = FeatureUnion([
        ("word_tfidf", text_word_pipe),
        ("char_tfidf", text_char_pipe),
        ("domain_features", DomainFeatureExtractor())
    ])

    return union
