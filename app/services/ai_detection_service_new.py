import numpy as np
im    def _initialize_models(self):
        """Initialise les modèles AI et ResNet50."""
        try:
            # Charger ResNet50 pour la extraction de features
            self.resnet_model = ResNet50(weights='imagenet', include_top=False, pooling='avg')
            logger.info("✅ Modèle ResNet50 chargé avec succès")

            # Note: Le modèle de détection AI sera entrainé plus tard
            logger.info("ℹ️ Mode développement: utilisation de ResNet50 pour la similarité uniquement")ow as tf
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.preprocessing import image
from sklearn.metrics.pairwise import cosine_similarity
from PIL import Image
import os
import logging
from typing import Dict, Any, Optional, Tuple
from app.utils.exceptions import AIDetectionError

logger = logging.getLogger(__name__)

class AIDetectionService:
    """Service pour la détection d'images générées par IA et la similarité d'images."""

    def __init__(self):
        self.ai_model = None
        self.resnet_model = None
        self._initialize_models()

    def _initialize_models(self):
        """Initialise les modèles AI et ResNet50."""
        try:
            # Charger le modèle de détection AI si disponible
            if os.path.exists(self.model_path):
                self.ai_model = tf.keras.models.load_model(self.model_path)
                logger.info("✅ Modèle de détection AI chargé avec succès")
            else:
                logger.warning(f"⚠️ Modèle AI non trouvé: {self.model_path}")

            # Charger ResNet50 pour l'extraction de caractéristiques
            self.resnet_model = ResNet50(weights="imagenet", include_top=False, pooling="avg")
            logger.info("✅ Modèle ResNet50 chargé avec succès")

        except Exception as e:
            logger.error(f"❌ Erreur lors du chargement des modèles: {str(e)}")
            self.ai_model = None
            self.resnet_model = None

    def detect_ai_image(self, image_path: str) -> Dict[str, Any]:
        """
        Détecte si une image a été générée par IA.

        Args:
            image_path: Chemin vers l'image à analyser

        Returns:
            Dictionnaire avec les résultats de détection
        """
        if not self.ai_model:
            return {
                "error": "Modèle AI non disponible",
                "is_ai_generated": False,
                "confidence": 0.0
            }

        try:
            # Charger et préprocesser l'image
            img = Image.open(image_path).convert("RGB")
            img = img.resize((128, 128), Image.Resampling.LANCZOS)
            img_array = np.array(img, dtype=np.float32) / 255.0
            img_array = np.expand_dims(img_array, axis=0)

            logger.debug(f"Image shape avant prédiction: {img_array.shape}")

            # Faire la prédiction
            prediction = self.ai_model.predict(img_array)
            confidence = float(prediction[0][0])
            is_ai_generated = confidence > 0.5

            logger.info(f"Détection AI - Confiance: {confidence:.4f}, IA générée: {is_ai_generated}")

            return {
                "is_ai_generated": bool(is_ai_generated),
                "confidence": confidence * 100,  # Convertir en pourcentage
                "threshold": 50.0
            }

        except Exception as e:
            logger.error(f"Erreur lors de la détection AI: {str(e)}")
            raise AIDetectionError(f"Erreur lors de la détection AI: {str(e)}")

    def extract_features(self, image_path: str) -> np.ndarray:
        """
        Extrait les caractéristiques d'une image avec ResNet50.

        Args:
            image_path: Chemin vers l'image

        Returns:
            Vecteur de caractéristiques
        """
        if not self.resnet_model:
            raise AIDetectionError("Modèle ResNet50 non disponible")

        try:
            # Charger l'image avec la taille requise pour ResNet50
            img = image.load_img(image_path, target_size=(224, 224))
            img_array = image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)
            img_array = preprocess_input(img_array)

            # Extraire les caractéristiques
            features = self.resnet_model.predict(img_array)
            return features.flatten()

        except Exception as e:
            logger.error(f"Erreur lors de l'extraction de caractéristiques: {str(e)}")
            raise AIDetectionError(f"Erreur lors de l'extraction de caractéristiques: {str(e)}")

    def compute_similarity(self, img1_path: str, img2_path: str) -> float:
        """
        Calcule la similarité cosinus entre deux images.

        Args:
            img1_path: Chemin vers la première image
            img2_path: Chemin vers la seconde image

        Returns:
            Score de similarité (0-1)
        """
        try:
            feat1 = self.extract_features(img1_path)
            feat2 = self.extract_features(img2_path)

            similarity = cosine_similarity([feat1], [feat2])[0][0]
            logger.info(f"Similarité cosinus calculée: {similarity:.4f}")

            return float(similarity)

        except Exception as e:
            logger.error(f"Erreur lors du calcul de similarité: {str(e)}")
            raise AIDetectionError(f"Erreur lors du calcul de similarité: {str(e)}")

    def find_similar_images_deep(self, image_path: str, image_list: list, threshold: float = 0.8) -> list:
        """
        Trouve des images similaires en utilisant les caractéristiques profondes.

        Args:
            image_path: Chemin vers l'image de référence
            image_list: Liste des images à comparer
            threshold: Seuil de similarité

        Returns:
            Liste des images similaires triée par similarité
        """
        try:
            ref_features = self.extract_features(image_path)
            similar_images = []

            for img_info in image_list:
                img_path = img_info.get('path') or img_info.get('image_path')
                if not img_path or not os.path.exists(img_path):
                    continue

                try:
                    similarity = self.compute_similarity(image_path, img_path)

                    if similarity >= threshold:
                        similar_images.append({
                            **img_info,
                            'similarity': similarity * 100,  # Convertir en pourcentage
                            'similarity_type': 'deep_features'
                        })

                except Exception as e:
                    logger.warning(f"Erreur lors de la comparaison avec {img_path}: {str(e)}")
                    continue

            return sorted(similar_images, key=lambda x: x['similarity'], reverse=True)

        except Exception as e:
            logger.error(f"Erreur lors de la recherche d'images similaires: {str(e)}")
            return []

    def is_available(self) -> Dict[str, bool]:
        """
        Vérifie la disponibilité des modèles.

        Returns:
            Dictionnaire indiquant quels modèles sont disponibles
        """
        return {
            "ai_detection": self.ai_model is not None,
            "resnet50": self.resnet_model is not None,
            "tensorflow": tf.__version__ if tf else None
        }
