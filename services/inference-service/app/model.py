# app/model.py
import torch
import torch.nn as nn
import torch.nn.functional as F

class VitalSignCNN(nn.Module):
    def __init__(self, num_features=3, num_classes=2):
        super(VitalSignCNN, self).__init__()
        self.conv1 = nn.Conv1d(num_features, 16, kernel_size=3, padding=1)
        self.conv2 = nn.Conv1d(16, 32, kernel_size=3, padding=1)
        self.fc1 = nn.Linear(32, 64)
        self.fc2 = nn.Linear(64, num_classes)
        self.dropout = nn.Dropout(0.3)

    def forward(self, x):
        # x shape: (batch, num_features, seq_len)
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = torch.mean(x, dim=2)  # global average pooling
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        return self.fc2(x)
