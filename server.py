import flwr as fl
import torch
from save_model import ProductivityNet  # Your existing model!

# Load your existing global model
global_model = ProductivityNet()
global_model.load_state_dict(torch.load('global_model.pth'))
global_model.eval()

def get_parameters(model):
    return [val.cpu().numpy() for val in model.state_dict().values()]

def set_parameters(model, parameters):
    params_dict = zip(model.state_dict().keys(), parameters)
    state_dict = {k: torch.tensor(v) for k,v in params_dict}
    model.load_state_dict(state_dict, strict=True)

class ActivityServer(fl.server.strategy.FedAvg):
    def __init__(self):
        super().__init__(
            fraction_fit=1.0,  # Sample 100% clients
            min_fit_clients=2,
            min_available_clients=2,
        )
    
    def aggregate_fit(
        self, server_round, results, failures
    ):
        """Aggregate client updates with FedAvg"""
        weights_results = [
            (fl.common.weights_to_parameters(w.parameters()), w.num_examples)
            for w in results
        ]
        aggregate_weights = fl.server.strategy.fedavg_weighted_aggregate(weights_results)
        return fl.server.strategy.FedAvg.aggregate_fit(self, server_round, results, failures)

strategy = ActivityServer()
print("🚀 Flower FL Server starting... (Uses your global_model.pth)")
fl.server.start_server(
    server_address="0.0.0.0:8080",
    config=fl.server.ServerConfig(num_rounds=10),
    strategy=strategy,
)
