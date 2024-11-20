import torch
import torch.nn as nn

class MNISTModel(nn.Module):
    def __init__(self):
        super(MNISTModel, self).__init__()
        
        self.features = nn.Sequential(
            nn.Conv2d(1, 8, kernel_size=3, padding=1),  # 28x28x8
            nn.ReLU(),
            nn.MaxPool2d(2),  # 14x14x8
            nn.Conv2d(8, 12, kernel_size=1),  # 14x14x16
            nn.ReLU(),
            nn.MaxPool2d(2),  # 7x7x16
            nn.Conv2d(12, 16, kernel_size=1),  # 7x7x32
        )
        
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(7 * 7 * 16, 10)
        )
        
    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x 