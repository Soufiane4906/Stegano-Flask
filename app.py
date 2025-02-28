import os
import uuid
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
from tensorflow.keras.models import load_model


app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

model = load_model("model.h5") if os.path.exists("model.h5") else None

# 📌 Endpoint: Upload d'une image + analyse
@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "Aucun fichier fourni"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Aucun fichier sélectionné"}), 400

    filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    steganography_result = analyze_steganography(filepath)
    ai_detection_result = detect_ai_image(filepath) if model else {"error": "Modèle AI non chargé"}
    metadata = get_image_metadata(filepath)

    return jsonify({
        "steganography": steganography_result,
        "ai_detection": ai_detection_result,
        "metadata": metadata
    })

def analyze_steganography(image_path):
    return {"signature_detected": True, "signature_type": "Exemple"}

def detect_ai_image(image_path):
    img = Image.open(image_path).resize((224, 224))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    prediction = model.predict(img_array) if model else [[0.0]]
    is_ai_generated = prediction[0][0] > 0.5

    return {"is_ai_generated": bool(is_ai_generated), "confidence": float(prediction[0][0] * 100)}

def get_image_metadata(image_path):
    img = Image.open(image_path)
    return {
        "dimensions": f"{img.width}x{img.height}",
        "format": img.format,
        "size": f"{os.path.getsize(image_path) / 1024:.2f} KB"
    }

if __name__ == '__main__':
    app.run(debug=True)
