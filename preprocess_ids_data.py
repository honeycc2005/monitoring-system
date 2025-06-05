from sklearn.preprocessing import StandardScaler
import numpy as np

# Load or define the same scaler used in training
scaler = StandardScaler()
scaler.mean_ = ...  # set manually or load from file
scaler.scale_ = ...

def preprocess_input(packet_features):
    # Ensure it's in the same format as training input
    x = np.array(packet_features).reshape(1, -1)
    x_scaled = scaler.transform(x)
    return x_scaled
