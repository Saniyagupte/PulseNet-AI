# services/inference-service/train_cnn.py

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import matplotlib.pyplot as plt
from model import VitalSignCNN
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# 1️⃣ Generate synthetic data
def generate_synthetic_vitals(n_samples=5000, seq_len=20):
    data = []
    labels = []

    for _ in range(n_samples):
        # Normal vitals
        heart = np.random.normal(80, 5, seq_len)
        spo2 = np.random.normal(98, 1, seq_len)
        resp = np.random.normal(16, 2, seq_len)

        # Randomly add anomaly
        if np.random.rand() < 0.3:  # 30% anomalous
            anomaly_type = np.random.choice(["hr", "spo2", "resp"])
            if anomaly_type == "hr":
                heart += np.random.choice([-40, +40])  # extreme HR
            elif anomaly_type == "spo2":
                spo2 -= np.random.choice([10, 15])
            elif anomaly_type == "resp":
                resp += np.random.choice([10, -6])
            label = 1
        else:
            label = 0

        data.append(np.stack([heart, spo2, resp], axis=0))  # shape: (3, seq_len)
        labels.append(label)

    return np.array(data, dtype=np.float32), np.array(labels, dtype=np.int64)

# 2️⃣ Prepare dataset
X, y = generate_synthetic_vitals()
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Convert to tensors
X_train, X_test = torch.tensor(X_train), torch.tensor(X_test)
y_train, y_test = torch.tensor(y_train), torch.tensor(y_test)

# 3️⃣ Model setup
model = VitalSignCNN(num_features=3, num_classes=2)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# 4️⃣ Training loop
EPOCHS = 15
train_losses = []

for epoch in range(EPOCHS):
    model.train()
    optimizer.zero_grad()
    outputs = model(X_train)
    loss = criterion(outputs, y_train)
    loss.backward()
    optimizer.step()
    train_losses.append(loss.item())
    print(f"Epoch [{epoch+1}/{EPOCHS}], Loss: {loss.item():.4f}")

# 5️⃣ Evaluate
model.eval()
with torch.no_grad():
    preds = model(X_test).argmax(dim=1)
    print("\nClassification Report:")
    print(classification_report(y_test, preds, target_names=["Normal", "Anomalous"]))

# 6️⃣ Plot loss curve
plt.plot(train_losses, label="Training Loss")
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.title("CNN Training Loss Curve")
plt.legend()
plt.show()

# 7️⃣ Save trained model
torch.save(model.state_dict(), "model.pt")
print("Model saved as model.pt")
