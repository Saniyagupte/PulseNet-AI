"""
model.py
--------
Defines deep learning architectures for healthcare event processing.
Currently includes:
- VitalSignCNN: 1D CNN for anomaly detection in vitals
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import logging

logger = logging.getLogger("model")


# --------------------------------------------------
# Base Model Interface (Optional future extensibility)
# --------------------------------------------------
class BaseVitalModel(nn.Module):
    """Base class to standardize vitals models."""
    def __init__(self):
        super().__init__()

    def forward(self, x):
        raise NotImplementedError("Subclasses must implement forward()")


# --------------------------------------------------
# CNN-based Vital Sign Anomaly Detector
# --------------------------------------------------
class VitalSignCNN(BaseVitalModel):
    """
    A 1D CNN for analyzing time-series or multi-sensor vital signs.
    Input shape: (batch_size, num_features, seq_len)
    """

    def __init__(self, num_features: int = 3, num_classes: int = 2):
        super().__init__()
        self.conv1 = nn.Conv1d(num_features, 16, kernel_size=3, padding=1)
        self.conv2 = nn.Conv1d(16, 32, kernel_size=3, padding=1)
        self.global_avg_pool = nn.AdaptiveAvgPool1d(1)
        self.fc1 = nn.Linear(32, 64)
        self.fc2 = nn.Linear(64, num_classes)
        self.dropout = nn.Dropout(0.3)

        logger.info(f"VitalSignCNN initialized with {num_features} features and {num_classes} classes.")

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through the CNN model.

        Args:
            x (Tensor): shape (batch, num_features, seq_len)
        Returns:
            Tensor: logits of shape (batch, num_classes)
        """
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = self.global_avg_pool(x).squeeze(2)  # global average pooling
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        out = self.fc2(x)
        return out


# --------------------------------------------------
# Future extensions placeholder
# --------------------------------------------------
# class VitalSignLSTM(BaseVitalModel):
#     ...
#
# class VitalSignTransformer(BaseVitalModel):
#     ...
