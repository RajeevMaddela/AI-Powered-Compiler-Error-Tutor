import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import joblib

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODELS_DIR = BASE_DIR / "ml" / "models"


class DiagnosticClassifier:
    """
    Production-ready inference wrapper for the trained C++ Compiler Error Classifier.
    Includes startup caching, calibrated confidence estimation, and graceful abstention.
    """
    _instance: Optional["DiagnosticClassifier"] = None

    def __init__(self):
        self.bundle: Optional[Dict[str, Any]] = None
        self.pipeline = None
        self.threshold: float = 0.55
        self.version: str = "none"
        self.classes: list = []
        self.load_active_model()

    @classmethod
    def get_instance(cls) -> "DiagnosticClassifier":
        if cls._instance is None:
            cls._instance = DiagnosticClassifier()
        return cls._instance

    def load_active_model(self) -> bool:
        pointer_file = MODELS_DIR / "active_model.json"
        if not pointer_file.exists():
            logger.warning("No active_model.json found in %s", MODELS_DIR)
            return False

        try:
            with open(pointer_file, "r", encoding="utf-8") as f:
                pointer = json.load(f)

            model_filename = pointer.get("active_file")
            model_path = MODELS_DIR / model_filename
            if not model_path.exists():
                logger.error("Active model file %s does not exist", model_path)
                return False

            self.bundle = joblib.load(model_path)
            self.pipeline = self.bundle["pipeline"]
            self.threshold = float(self.bundle.get("threshold", 0.55))
            self.version = str(self.bundle.get("version", "v1.0.0"))
            self.classes = list(self.bundle.get("classes", []))
            logger.info("Loaded active error model version: %s (threshold: %.2f)", self.version, self.threshold)
            return True
        except Exception as e:
            logger.error("Failed to load active model: %s", e)
            return False

    def predict(self, diagnostic_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classifies a single diagnostic record.
        Returns:
            category: str
            confidence: float (0.0 to 1.0)
            abstained: bool
            model_version: str
            top_classes: list of (class, prob)
        """
        if self.pipeline is None:
            # Fallback if no model is loaded yet
            return {
                "category": None,
                "confidence": 0.0,
                "abstained": True,
                "model_version": "none",
                "top_classes": []
            }

        # Predict with calibrated probabilities
        probs = self.pipeline.predict_proba([diagnostic_record])[0]
        max_idx = int(probs.argmax())
        max_prob = float(probs[max_idx])
        pred_category = str(self.classes[max_idx])

        # Graceful abstention when confidence is below calibrated threshold
        abstained = bool(max_prob < self.threshold)

        # Ranked classes
        top_indices = probs.argsort()[::-1][:3]
        top_classes = [{"category": str(self.classes[i]), "confidence": round(float(probs[i]), 4)} for i in top_indices]

        return {
            "category": pred_category,
            "confidence": round(max_prob, 4),
            "abstained": abstained,
            "model_version": self.version,
            "top_classes": top_classes
        }


# Global singleton helper
def get_classifier() -> DiagnosticClassifier:
    return DiagnosticClassifier.get_instance()

