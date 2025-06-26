import os
import uuid
import numpy as np
import cv2
import tensorflow as tf
from stegano import lsb
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from PIL import Image
import hashlib
import sqlite3
import imagehash
import time
from datetime import datetime
from scipy.spatial.distance import hamming

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
DATABASE_PATH = 'images.db'
SIMILARITY_THRESHOLD = 0.85  # 85% similarity threshold for perceptual hashing
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load AI Model
MODEL_PATH = "modelFakeReal.h5"
model = None
if os.path.exists(MODEL_PATH):
    model = tf.keras.models.load_model(MODEL_PATH)

# Initialize database
def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        image_path TEXT NOT NULL,
        phash TEXT NOT NULL,
        dhash TEXT NOT NULL,
        cv_signature TEXT NOT NULL,
        metadata TEXT NOT NULL,
        user_signature TEXT,
        is_ai_generated BOOLEAN,
        ai_confidence REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()

# Generate database connection helper
def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Initialize database on startup
init_db()

# 📌 Generate Perceptual Hashes
def generate_image_hashes(image_path):
    try:
        img = Image.open(image_path)

        # Generate perceptual hash (pHash)
        phash = str(imagehash.phash(img))

        # Generate difference hash (dHash)
        dhash = str(imagehash.dhash(img))

        return {
            "phash": phash,
            "dhash": dhash
        }
    except Exception as e:
        return {"error": f"Failed to generate hashes: {str(e)}"}

# 📌 Find Similar Images in Database
def find_similar_images(hashes):
    conn = get_db_connection()
    cursor = conn.cursor()

    similar_images = []

    try:
        # Get all images from database
        cursor.execute("SELECT id, filename, phash, dhash, image_path FROM images")
        all_images = cursor.fetchall()

        for img in all_images:
            # Calculate Hamming distance for both pHash and dHash
            phash_similarity = 1 - hamming(
                [int(bit) for bit in hashes["phash"]],
                [int(bit) for bit in img["phash"]]
            )

            dhash_similarity = 1 - hamming(
                [int(bit) for bit in hashes["dhash"]],
                [int(bit) for bit in img["dhash"]]
            )

            # Average the similarities
            avg_similarity = (phash_similarity + dhash_similarity) / 2

            if avg_similarity >= SIMILARITY_THRESHOLD:
                similar_images.append({
                    "id": img["id"],
                    "filename": img["filename"],
                    "image_path": img["image_path"],
                    "similarity": avg_similarity * 100  # Convert to percentage
                })
    except Exception as e:
        print(f"Error finding similar images: {str(e)}")

    conn.close()
    return similar_images

# 📌 Save Image Data to Database
def save_image_to_db(image_data):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO images (
        filename, image_path, phash, dhash, cv_signature,
        metadata, user_signature, is_ai_generated, ai_confidence
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        image_data["filename"],
        image_data["image_path"],
        image_data["phash"],
        image_data["dhash"],
        image_data["cv_signature"],
        image_data["metadata_json"],
        image_data.get("user_signature"),
        image_data.get("is_ai_generated"),
        image_data.get("ai_confidence")
    ))

    image_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return image_id

# 📌 Image Upload + Analysis (Steganography & AI Detection)
@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "Aucun fichier fourni"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Aucun fichier sélectionné"}), 400

    # Create a temporary file to analyze before deciding to save
    temp_filename = "temp_" + str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
    temp_filepath = os.path.join(UPLOAD_FOLDER, temp_filename)
    file.save(temp_filepath)

    # Generate hashes
    hashes = generate_image_hashes(temp_filepath)

    # Check for similar images in database
    similar_images = find_similar_images(hashes)

    # Only proceed with full analysis if similars check is requested or no similar images
    skip_analysis = request.args.get('skip_analysis') == 'true'
    only_check_similar = request.args.get('only_check_similar') == 'true'

    if only_check_similar:
        os.remove(temp_filepath)  # Remove temp file
        return jsonify({
            "similar_images": similar_images,
            "similar_found": len(similar_images) > 0
        })

    # Generate permanent filename
    filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    # Rename temp file to permanent name
    os.rename(temp_filepath, filepath)

    # Continue with full analysis
    steganography_result = analyze_steganography(filepath)
    ai_detection_result = detect_ai_image(filepath) if model else {"error": "Modèle AI non chargé"}
    metadata = get_image_metadata(filepath)

    # Generate image context signature
    context_signature = generate_image_context_signature(filepath)

    # Prepare data for database
    image_data = {
        "filename": os.path.basename(file.filename),
        "image_path": filepath,
        "phash": hashes["phash"],
        "dhash": hashes["dhash"],
        "cv_signature": context_signature,
        "metadata_json": str(metadata),
        "is_ai_generated": ai_detection_result.get("is_ai_generated", False) if isinstance(ai_detection_result, dict) else False,
        "ai_confidence": ai_detection_result.get("confidence", 0) if isinstance(ai_detection_result, dict) else 0
    }

    # Save to database
    image_id = save_image_to_db(image_data)

    return jsonify({
        "image_id": image_id,
        "filename": filename,
        "steganography": steganography_result,
        "ai_detection": ai_detection_result,
        "metadata": metadata,
        "image_path": filepath,
        "context_signature": context_signature,
        "perceptual_hashes": hashes,
        "similar_images": similar_images,
        "similar_found": len(similar_images) > 0
    })

# 📌 Add Hidden Signature (Steganography)
@app.route('/add_steganography', methods=['POST'])
def add_steganography():
    if 'file' not in request.files:
        return jsonify({"error": "Fichier manquant"}), 400

    file = request.files['file']

    # Get user signature if provided, otherwise use empty string
    user_signature = request.form.get('signature', '')

    # Create a temporary file to analyze before deciding to save
    temp_filename = "temp_" + str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
    temp_filepath = os.path.join(UPLOAD_FOLDER, temp_filename)
    file.save(temp_filepath)

    # Generate hashes for similarity check
    hashes = generate_image_hashes(temp_filepath)

    # Check for similar images in database
    similar_images = find_similar_images(hashes)

    # Generate permanent filename
    filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    # Rename temp file to permanent name
    os.rename(temp_filepath, filepath)

    # Generate image context signature
    context_signature = generate_image_context_signature(filepath)

    # Combine user signature with context signature if user signature exists
    if user_signature:
        combined_signature = f"{user_signature}||{context_signature}"
    else:
        combined_signature = context_signature

    output_filepath = embed_steganography(filepath, combined_signature)

    # Analyze the output image for AI detection
    ai_detection_result = detect_ai_image(output_filepath) if model else {"error": "Modèle AI non chargé"}
    metadata = get_image_metadata(output_filepath)

    # Generate new hashes for the output image with steganography
    output_hashes = generate_image_hashes(output_filepath)

    # Prepare data for database
    image_data = {
        "filename": os.path.basename(file.filename),
        "image_path": output_filepath,
        "phash": output_hashes["phash"],
        "dhash": output_hashes["dhash"],
        "cv_signature": context_signature,
        "metadata_json": str(metadata),
        "user_signature": user_signature,
        "is_ai_generated": ai_detection_result.get("is_ai_generated", False) if isinstance(ai_detection_result, dict) else False,
        "ai_confidence": ai_detection_result.get("confidence", 0) if isinstance(ai_detection_result, dict) else 0
    }

    # Save to database
    image_id = save_image_to_db(image_data)

    # Convert Windows-style `\` to `/` and return a public URL
    output_filename = os.path.basename(output_filepath)
    public_url = f"http://localhost:5000/uploads/{output_filename}"

    return jsonify({
        "message": "Signature ajoutée avec succès",
        "image_url": public_url,
        "image_id": image_id,
        "context_signature": context_signature,
        "similar_images": similar_images,
        "similar_found": len(similar_images) > 0
    })

# 📌 List All Images
@app.route('/images', methods=['GET'])
def list_images():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, filename, image_path, phash, dhash, cv_signature,
           timestamp, is_ai_generated, ai_confidence
    FROM images ORDER BY timestamp DESC
    ''')

    images = cursor.fetchall()
    conn.close()

    result = []
    for img in images:
        result.append({
            "id": img["id"],
            "filename": img["filename"],
            "image_path": img["image_path"],
            "image_url": f"http://localhost:5000/uploads/{os.path.basename(img['image_path'])}",
            "phash": img["phash"],
            "dhash": img["dhash"],
            "cv_signature": img["cv_signature"],
            "timestamp": img["timestamp"],
            "is_ai_generated": bool(img["is_ai_generated"]),
            "ai_confidence": img["ai_confidence"]
        })

    return jsonify({"images": result})

# 📌 Get Image Details
@app.route('/images/<int:image_id>', methods=['GET'])
def get_image_details(image_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
    SELECT * FROM images WHERE id = ?
    ''', (image_id,))

    img = cursor.fetchone()
    conn.close()

    if not img:
        return jsonify({"error": "Image not found"}), 404

    # Find similar images
    hashes = {
        "phash": img["phash"],
        "dhash": img["dhash"]
    }
    similar_images = find_similar_images(hashes)

    # Filter out the current image from similars
    similar_images = [s for s in similar_images if s["id"] != image_id]

    return jsonify({
        "id": img["id"],
        "filename": img["filename"],
        "image_path": img["image_path"],
        "image_url": f"http://localhost:5000/uploads/{os.path.basename(img['image_path'])}",
        "phash": img["phash"],
        "dhash": img["dhash"],
        "cv_signature": img["cv_signature"],
        "metadata": img["metadata"],
        "user_signature": img["user_signature"],
        "is_ai_generated": bool(img["is_ai_generated"]),
        "ai_confidence": img["ai_confidence"],
        "timestamp": img["timestamp"],
        "similar_images": similar_images
    })

# 📌 Generate Image Context Signature
def generate_image_context_signature(image_path):
    try:
        # Read the image
        img = cv2.imread(image_path)
        if img is None:
            return "Failed to read image"

        # Convert to grayscale for feature extraction
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 1. Extract dominant colors (from original color image)
        pixels = np.float32(img.reshape(-1, 3))
        n_colors = 5
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, 0.1)
        _, labels, centers = cv2.kmeans(pixels, n_colors, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        dominant_colors = centers.astype(np.int32).tolist()

        # 2. Extract key features using ORB (Oriented FAST and Rotated BRIEF)
        orb = cv2.ORB_create(nfeatures=20)
        keypoints, descriptors = orb.detectAndCompute(gray, None)

        # If no descriptors found, use alternative method
        if descriptors is None or len(keypoints) < 5:
            # Use edge detection instead
            edges = cv2.Canny(gray, 100, 200)
            feature_hash = hashlib.sha256(edges.tobytes()).hexdigest()
        else:
            # Create a fingerprint from descriptors
            feature_hash = hashlib.sha256(descriptors.tobytes()).hexdigest()

        # 3. Calculate image statistics
        brightness = np.mean(gray)
        contrast = np.std(gray)

        # 4. Get image dimensions
        height, width = img.shape[:2]

        # Combine all features into a signature
        signature_data = {
            "dominant_colors": dominant_colors[:3],  # Use top 3 colors only
            "feature_hash": feature_hash[:16],       # Use first 16 chars of hash
            "brightness": round(brightness, 2),
            "contrast": round(contrast, 2),
            "dimensions": f"{width}x{height}"
        }

        # Create a compact signature string
        compact_signature = f"CV:{feature_hash[:16]}:{brightness:.1f}:{contrast:.1f}:{width}x{height}"

        return compact_signature

    except Exception as e:
        return f"Error generating signature: {str(e)}"

# 📌 Verify Context Signature
@app.route('/verify_signature', methods=['POST'])
def verify_signature():
    if 'file' not in request.files:
        return jsonify({"error": "Fichier manquant"}), 400

    file = request.files['file']
    filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    # Generate hashes for similarity check
    hashes = generate_image_hashes(filepath)

    # Check for similar images in database
    similar_images = find_similar_images(hashes)

    # Check for embedded steganography
    steg_result = analyze_steganography(filepath)

    # Generate current image context signature
    current_context_signature = generate_image_context_signature(filepath)

    # Extract context signature from steganography if available
    embedded_signature = steg_result.get("signature", "")
    embedded_context_signature = ""
    user_signature = ""

    if embedded_signature and "||" in embedded_signature:
        # Split combined signature format: "user_sig||context_sig"
        user_signature, embedded_context_signature = embedded_signature.split("||", 1)
    elif embedded_signature and embedded_signature.startswith("CV:"):
        # Only context signature was embedded
        embedded_context_signature = embedded_signature

    # Compare signatures
    signatures_match = embedded_context_signature == current_context_signature

    return jsonify({
        "steganography_detected": steg_result.get("signature_detected", False),
        "current_context_signature": current_context_signature,
        "embedded_context_signature": embedded_context_signature,
        "user_signature": user_signature,
        "signatures_match": signatures_match,
        "tampered": bool(embedded_context_signature and not signatures_match),
        "similar_images": similar_images,
        "similar_found": len(similar_images) > 0
    })

# 📌 Steganography Analysis (Detect Hidden Message)
def analyze_steganography(image_path):
    try:
        hidden_message = lsb.reveal(image_path)
        return {"signature_detected": True, "signature": hidden_message} if hidden_message else {"signature_detected": False}
    except Exception as e:
        return {"error": "Impossible to detect message."}

@app.route('/uploads/<filename>')
def get_uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# 📌 Steganography Embedding (Hide Message)
def embed_steganography(image_path, signature):
    output_path = image_path.replace(".", "_steg.")
    try:
        hidden_image = lsb.hide(image_path, signature)
        hidden_image.save(output_path)
        return output_path
    except Exception as e:
        return str(e)

# 📌 AI-Generated Image Detection
def detect_ai_image(image_path):
    try:
        img = Image.open(image_path).convert("RGB")  # 🔹 Convertir en RGB pour éviter les erreurs de format
        img = img.resize((128, 128), Image.Resampling.LANCZOS)  # 🔹 Redimensionner correctement
        img_array = np.array(img, dtype=np.float32) / 255.0  # 🔹 Normalisation correcte
        img_array = np.expand_dims(img_array, axis=0)  # 🔹 Ajouter une dimension batch

        print(f"DEBUG - Image shape before prediction: {img_array.shape}")  # Devrait être (1, 128, 128, 3)

        prediction = model.predict(img_array) if model else [[0.0]]
        is_ai_generated = prediction[0][0] > 0.5

        return {"is_ai_generated": bool(is_ai_generated), "confidence": float(prediction[0][0] * 100)}
    except Exception as e:
        return {"error": str(e)}

# 📌 Image Metadata Extraction
def get_image_metadata(image_path):
    img = Image.open(image_path)
    return {
        "dimensions": f"{img.width}x{img.height}",
        "format": img.format,
        "size": f"{os.path.getsize(image_path) / 1024:.2f} KB"
    }

if __name__ == '__main__':
    app.run(debug=True)