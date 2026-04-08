import torch
import torch.nn as nn
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, roc_curve, auc
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

print("🚀 Training started...")

device = torch.device("cpu")

# 🔥 TRANSFORM (slightly improved for better accuracy)
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
])

# Load dataset
train_data = datasets.ImageFolder("dataset_split/train", transform=transform)
test_data = datasets.ImageFolder("dataset_split/test", transform=transform)

# 🔥 Limit data (FAST but still accurate)
train_data.samples = train_data.samples[:2000]
test_data.samples = test_data.samples[:500]

train_loader = DataLoader(train_data, batch_size=4, shuffle=True, num_workers=0)
test_loader = DataLoader(test_data, batch_size=4, num_workers=0)

# 🔥 MODEL (best balance)
model = models.resnet18(pretrained=True)
model.fc = nn.Linear(model.fc.in_features, 4)
model = model.to(device)

criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)

epochs = 6   # slightly increased for better accuracy
train_losses = []

# 🔥 TRAINING
for epoch in range(epochs):
    print(f"🔥 Epoch {epoch+1}")
    model.train()
    total_loss = 0

    for images, labels in train_loader:
        images, labels = images.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    train_losses.append(total_loss)
    print(f"Loss: {total_loss:.4f}")

# 🔥 SAVE MODEL (IMPORTANT)
torch.save(model.state_dict(), "model.pth")
print("✅ Model saved as model.pth")

# 🔥 EVALUATION
model.eval()
preds, targets = [], []
probs = []

with torch.no_grad():
    for images, labels in test_loader:
        images = images.to(device)
        outputs = model(images)

        probabilities = torch.softmax(outputs, dim=1)
        _, predicted = torch.max(outputs, 1)

        preds.extend(predicted.cpu().numpy())
        targets.extend(labels.numpy())
        probs.extend(probabilities.cpu().numpy())

# 🔥 ACCURACY
accuracy = accuracy_score(targets, preds)
print(f"\n🎯 Accuracy: {accuracy*100:.2f}%")

# 🔥 CLASSIFICATION REPORT
print("\n📊 Classification Report:")
print(classification_report(
    targets,
    preds,
    labels=[0,1,2,3],
    target_names=train_data.classes,
    zero_division=0
))

# 🔥 CONFUSION MATRIX
cm = confusion_matrix(targets, preds, labels=[0,1,2,3])

plt.figure(figsize=(6,5))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=train_data.classes,
            yticklabels=train_data.classes)
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix")
plt.savefig("confusion_matrix.png")
print("✅ Saved: confusion_matrix.png")

# 🔥 ROC CURVE (FAST)
targets_bin = np.eye(4)[targets]
probs = np.array(probs)

fpr, tpr, _ = roc_curve(targets_bin.ravel(), probs.ravel())
roc_auc = auc(fpr, tpr)

plt.figure()
plt.plot(fpr, tpr, label=f"AUC = {roc_auc:.2f}")
plt.plot([0,1],[0,1],'k--')
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curve")
plt.legend()
plt.savefig("roc_curve.png")
print("✅ Saved: roc_curve.png")

# 🔥 LOSS GRAPH
plt.figure()
plt.plot(train_losses, marker='o')
plt.title("Training Loss")
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.savefig("loss.png")
print("✅ Saved: loss.png")