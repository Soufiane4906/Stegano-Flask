import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.preprocessing import image
from sklearn.metrics.pairwise import cosine_similarity

# Load the pre-trained ResNet50 model without the classification head
model = ResNet50(weights="imagenet", include_top=False, pooling="avg")

def extract_features(img_path, model):
    """Extract feature vector from an image using ResNet50."""
    img = image.load_img(img_path, target_size=(224, 224))  # Resize to model input size
    img_array = image.img_to_array(img)  # Convert to array
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    img_array = preprocess_input(img_array)  # Normalize using ResNet50 preprocessing
    features = model.predict(img_array)  # Extract features
    return features.flatten()  # Flatten to 1D vector

def compute_similarity(img1_path, img2_path):
    """Compute cosine similarity between two images."""
    feat1 = extract_features(img1_path, model)
    feat2 = extract_features(img2_path, model)
    similarity = cosine_similarity([feat1], [feat2])[0][0]  # Compute cosine similarity
    return similarity

# Example usage:
img1 = "uploads\ed1ee562-3f01-46a2-9667-4007764632af.png"  # Replace with your image path
img2 = "uploads\ed1ee562-3f01-46a2-9667-4007764632af.png"  # Replace with your image path
similarity_score = compute_similarity(img1, img2)
print(f"Cosine Similarity: {similarity_score:.4f}")
