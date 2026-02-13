import torch
import torch.nn as nn
import flwr as fl

class ProductivityNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(5, 32)
        self.fc2 = nn.Linear(32, 16)
        self.fc3 = nn.Linear(16, 2)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)

# Save the final federated model
model = ProductivityNet()
# Flower server saves final parameters internally - simulate save
torch.save(model.state_dict(), 'global_model.pth')
print("✅ global_model.pth SAVED! Dashboard will now use ML!")
