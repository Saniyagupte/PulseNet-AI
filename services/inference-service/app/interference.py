# app/inference.py
import torch
import torch.nn.functional as F
from .model import VitalSignCNN

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# load trained model weights
MODEL_PATH = "app/models/vitals_cnn.pt"

model = VitalSignCNN(num_features=3, num_classes=2).to(DEVICE)
model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
model.eval()

def predict(vitals):
    """
    vitals: dict like {"heart_rate": 85, "oxygen": 96, "blood_pressure": 120}
    """
    try:
        x = torch.tensor([[vitals["heart_rate"], vitals["oxygen"], vitals["blood_pressure"]]], dtype=torch.float32)
        x = x.unsqueeze(2).to(DEVICE)  # shape (batch=1, features=3, seq_len=1)
        with torch.no_grad():
            logits = model(x)
            probs = F.softmax(logits, dim=1)
            score = float(probs[0, 1])  # anomaly probability
            label = "anomaly" if score > 0.7 else "normal"
            return {"label": label, "score": score}
    except Exception as e:
        return {"label": "error", "score": 0, "error": str(e)}
