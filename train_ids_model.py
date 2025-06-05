import torch
import torch.nn as nn
import torch.optim as optim
from ids_model import IDSModel
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# 1. Generate dummy data (replace with actual network data if available)
X, y = make_classification(n_samples=1000, n_features=41, n_informative=30, n_classes=2)
scaler = StandardScaler()
X = scaler.fit_transform(X)

# 2. Train/Test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# 3. Convert to torch tensors
X_train = torch.tensor(X_train).float()
y_train = torch.tensor(y_train).float().unsqueeze(1)

# 4. Initialize model
model = IDSModel(input_size=41)
criterion = nn.BCELoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# 5. Train the model
for epoch in range(20):
    optimizer.zero_grad()
    output = model(X_train)
    loss = criterion(output, y_train)
    loss.backward()
    optimizer.step()
    print(f"Epoch {epoch+1}, Loss: {loss.item():.4f}")

# 6. Save the model
torch.save(model.state_dict(), "ids_model.pth")
print("✅ Model saved as ids_model.pth")
