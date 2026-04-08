from flask import Flask, render_template, request
import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image

app = Flask(__name__)

# 🔥 Load trained model
model = models.resnet18(pretrained=False)
model.fc = nn.Linear(model.fc.in_features, 4)
model.load_state_dict(torch.load("model.pth", map_location="cpu"))
model.eval()

# Class labels (must match training)
classes = ['Mild_Demented', 'Moderate_Demented', 'Non_Demented', 'Very_Mild_Demented']

# Image preprocessing
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

# 🟢 Home route
@app.route('/')
def home():
    return render_template("index.html")

# 🟢 Prediction route
@app.route('/predict', methods=['POST'])
def predict():
    file = request.files['file']

    if file.filename == '':
        return render_template("index.html", prediction="No file selected")

    # Load image
    img = Image.open(file).convert('RGB')
    img = transform(img).unsqueeze(0)

    # Predict
    with torch.no_grad():
        output = model(img)
        probabilities = torch.softmax(output, dim=1)
        confidence, pred = torch.max(probabilities, 1)

    result = classes[pred.item()]
    confidence = round(confidence.item() * 100, 2)

    # 🔥 Patient-friendly explanation
    explanations = {
        "Non_Demented": "🟢 No signs of Alzheimer’s detected. Brain appears normal.",
        "Very_Mild_Demented": "🟡 Very mild signs detected. Early monitoring is recommended.",
        "Mild_Demented": "🟠 Mild Alzheimer’s detected. Medical consultation is advised.",
        "Moderate_Demented": "🔴 Moderate Alzheimer’s detected. Immediate medical attention is recommended."
    }

    message = explanations.get(result, "")

    return render_template(
        "index.html",
        prediction=result,
        confidence=confidence,
        message=message
    )

# 🟢 Run app
if __name__ == "__main__":
    app.run(debug=True)