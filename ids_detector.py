import torch
from ids_model import IDSModel
from preprocess_ids_data import preprocess_input  # You'll define this

# Load the trained model
model = IDSModel(input_size=41)
model.load_state_dict(torch.load("ids_model.pth"))
model.eval()

def detect_intrusion(packet_features):
    x = preprocess_input(packet_features)  # Format your packet features
    with torch.no_grad():
        output = model(torch.tensor(x).float())
    return output.item() > 0.5
