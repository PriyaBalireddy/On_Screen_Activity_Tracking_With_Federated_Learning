import flwr as fl
import torch
import numpy as np
from save_model import ProductivityNet
import time

# Your existing model
model = ProductivityNet()

# Simulated activity data (from tracker.py)
activity_features = []  # [app_features, duration, time_of_day, etc.]
activity_labels = []    # 0=unproductive, 1=productive

def get_activity_features(app_name, duration):
    """Convert tracker data → ML features"""
    features = np.array([
        1.0 if 'code' in app_name.lower() else 0.0,
        1.0 if 'youtube' in app_name.lower() else 0.0,
        1.0 if duration > 300 else 0.0,
        len(app_name) / 20.0,
        time.time() % 86400 / 86400  # Time of day
    ], dtype=np.float32)
    label = 1 if 'code' in app_name.lower() else 0  # Binary classification
    return features, label

class ActivityClient(fl.client.NumPyClient):
    def get_parameters(self, config):
        return [val.cpu().numpy() for val in model.state_dict().values()]

    def set_parameters(self, parameters):
        params_dict = zip(model.state_dict().keys(), parameters)
        state_dict = {k: torch.tensor(v) for k, v in params_dict}
        model.load_state_dict(state_dict, strict=True)

    def fit(self, parameters, config):
        # Load global model
        self.set_parameters(parameters)
        
        # Train on local activity data
        if len(activity_features) > 0:
            X = torch.tensor(activity_features)
            y = torch.tensor(activity_labels)
            
            optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
            criterion = torch.nn.CrossEntropyLoss()
            
            model.train()
            for epoch in range(3):  # Local epochs
                optimizer.zero_grad()
                outputs = model(X)
                loss = criterion(outputs, y)
                loss.backward()
                optimizer.step()
            
            print(f"✅ Client trained on {len(activity_features)} samples")
            return self.get_parameters(config), len(activity_features), {}
        
        return self.get_parameters(config), 0, {}

    def evaluate(self, parameters, config):
        self.set_parameters(parameters)
        model.eval()
        # Placeholder evaluation
        return 0.0, len(activity_features), {"accuracy": 0.85}

def start_client():
    fl.client.start_numpy_client(server_address="127.0.0.1:8080")

if __name__ == '__main__':
    start_client()
