"""
Inference Module
----------------
Handles model loading and anomaly detection predictions
for patient vitals data using a trained PyTorch CNN.
"""

import os
import torch
import torch.nn.functional as F
import logging
from app.model import VitalSignCNN

# --------------------------------------------------
# Logging
# --------------------------------------------------
logger = logging.getLogger("inference-model")

# --------------------------------------------------
# Device Configuration
# --------------------------------------------------
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


class ModelService:
    """Encapsulates model loading and inference logic."""

    def __init__(self, model_path: str = "app/models/vitals_cnn.pt"):
        self.model_path = model_path
        self.model = None
        self.load_model()

    def load_model(self):
        """Load the trained CNN model from disk."""
        if not os.path.exists(self.model_path):
            logger.warning(f"Model file not found at {self.model_path}. Starting in degraded mode.")
            self.model = None
            return

        self.model = VitalSignCNN(num_features=3, num_classes=2).to(DEVICE)
        try:
            self.model.load_state_dict(torch.load(self.model_path, map_location=DEVICE))
            self.model.eval()
            logger.info(f"Model loaded successfully from {self.model_path} on {DEVICE.upper()}")
        except Exception as e:
            logger.exception(f"Failed to load model: {e}")
            self.model = None

    def predict(self, vitals: dict) -> dict:
        """
        Perform model inference.

        Args:
            vitals (dict): {"heart_rate": 85, "oxygen": 96, "blood_pressure": 120}

        Returns:
            dict: {"label": "anomaly"|"normal", "score": float, "anomaly": bool}
        """
        if not self.model:
            return {"label": "error", "score": 0.0, "anomaly": False, "error": "Model not loaded"}

        try:
            # Prepare input tensor
            x = torch.tensor(
                [[vitals.get("heart_rate", 80), vitals.get("oxygen", 98), vitals.get("blood_pressure", 120)]],
                dtype=torch.float32
            ).unsqueeze(2).to(DEVICE)

            with torch.no_grad():
                logits = self.model(x)
                probs = F.softmax(logits, dim=1)
                score = float(probs[0, 1])  # anomaly probability

            anomaly = score > 0.7
            label = "anomaly" if anomaly else "normal"

            return {
                "label": label,
                "score": round(score, 4),
                "anomaly": anomaly
            }

        except Exception as e:
            logger.exception("Inference failed")
            return {"label": "error", "score": 0.0, "anomaly": False, "error": str(e)}


# --------------------------------------------------
# Global Model Service Instance
# --------------------------------------------------
_model_service = ModelService()


def predict(vitals: dict) -> dict:
    """Public function used by FastAPI and Kafka consumers."""
    return _model_service.predict(vitals)
