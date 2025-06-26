import os
from typing import Dict, Any, Optional
import logging
from app.utils.exceptions import AIDetectionError

# Import conditionnel de TensorFlow et des dépendances
try:
    import tensorflow as tf
    import numpy as np
    from tensorflow.keras.applications import ResNet50
    from tensorflow.keras.applications.resnet50 import preprocess_input
    from tensorflow.keras.preprocessing import image
    from sklearn.metrics.pairwise import cosine_similarity
    from PIL import Image
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    tf = None
    np = None
    Image = None

logger = logging.getLogger(__name__)

class AIDetectionService:
    """Service pour la détection d'images générées par IA et la similarité d'images."""

    def __init__(self):
        self.ai_model = None
        self.resnet_model = None

        if not TENSORFLOW_AVAILABLE:
            logger.warning("⚠️ TensorFlow n'est pas disponible. Fonctionnalités IA limitées.")
            return

        self._initialize_models()

    def _initialize_models(self):
        """Initialise les modèles AI et ResNet50."""
        if not TENSORFLOW_AVAILABLE:
            return

        try:
            # Charger ResNet50 pour l'extraction de caractéristiques
            self.resnet_model = ResNet50(weights="imagenet", include_top=False, pooling="avg")
            logger.info("✅ Modèle ResNet50 chargé avec succès")

            # Charger le modèle de détection IA personnalisé
            model_path = "model.h5"
            if os.path.exists(model_path):
                try:
                    # Tentative de chargement avec compile=False pour éviter les erreurs de compatibilité
                    self.ai_model = tf.keras.models.load_model(model_path, compile=False)
                    logger.info(f"✅ Modèle de détection IA chargé: {model_path}")
                except Exception as e:
                    logger.warning(f"⚠️ Impossible de charger le modèle {model_path}: {e}")
                    logger.info("🔄 Mode fallback activé - détection IA désactivée")
                    self.ai_model = None
            else:
                logger.info("ℹ️ Modèle personnalisé non trouvé, mode fallback activé")
                self.ai_model = None

        except Exception as e:
            logger.error(f"❌ Erreur lors du chargement des modèles: {str(e)}")
            self.ai_model = None
            self.resnet_model = None

    def detect_ai_image(self, image_path: str) -> Dict[str, Any]:
        """
        Détecte si une image a été générée par IA (implémentation exacte de steganoV2.py).

        Args:
            image_path: Chemin vers l'image à analyser

        Returns:
            Dictionnaire avec les résultats de détection
        """
        try:
            if not self.ai_model:
                # Mode fallback - retourner une réponse indicative
                return {
                    "is_ai_generated": False,
                    "confidence": 0.0,
                    "confidence_percentage": 0.0,
                    "status": "model_unavailable",
                    "message": "Modèle de détection IA non disponible - mode fallback actif"
                }

            img = Image.open(image_path).convert("RGB")  # 🔹 Convertir en RGB pour éviter les erreurs de format
            img = img.resize((128, 128), Image.Resampling.LANCZOS)  # 🔹 Redimensionner correctement
            img_array = np.array(img, dtype=np.float32) / 255.0  # 🔹 Normalisation correcte
            img_array = np.expand_dims(img_array, axis=0)  # 🔹 Ajouter une dimension batch

            logger.debug(f"DEBUG - Image shape before prediction: {img_array.shape}")  # Devrait être (1, 128, 128, 3)

            prediction = self.ai_model.predict(img_array)
            is_ai_generated = prediction[0][0] > 0.5

            return {
                "is_ai_generated": bool(is_ai_generated),
                "confidence": float(prediction[0][0] * 100)
            }
        except Exception as e:
            logger.error(f"Erreur lors de la détection IA: {str(e)}")
            return {"error": str(e)}

    def extract_features(self, image_path: str) -> Any:
        """
        Extrait les caractéristiques d'une image avec ResNet50.

        Args:
            image_path: Chemin vers l'image

        Returns:
            Vecteur de caractéristiques ou None si non disponible
        """
        if not TENSORFLOW_AVAILABLE or not self.resnet_model:
            logger.warning("ResNet50 non disponible pour l'extraction de caractéristiques")
            return None

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
            return None

    def compute_similarity(self, img1_path: str, img2_path: str) -> float:
        """
        Calcule la similarité cosinus entre deux images.

        Args:
            img1_path: Chemin vers la première image
            img2_path: Chemin vers la seconde image

        Returns:
            Score de similarité (0-1)
        """
        if not TENSORFLOW_AVAILABLE:
            return 0.5  # Valeur par défaut

        try:
            feat1 = self.extract_features(img1_path)
            feat2 = self.extract_features(img2_path)

            if feat1 is None or feat2 is None:
                return 0.5

            similarity = cosine_similarity([feat1], [feat2])[0][0]
            logger.info(f"Similarité cosinus calculée: {similarity:.4f}")

            return float(similarity)

        except Exception as e:
            logger.error(f"Erreur lors du calcul de similarité: {str(e)}")
            return 0.5

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
        if not TENSORFLOW_AVAILABLE:
            return []

        try:
            ref_features = self.extract_features(image_path)
            if ref_features is None:
                return []

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

    def _simulate_ai_detection(self, image_path: str) -> Dict[str, Any]:
        """
        Simulation de détection IA quand TensorFlow n'est pas disponible.

        Args:
            image_path: Chemin vers l'image

        Returns:
            Résultats simulés
        """
        # Simulation basée sur la taille du fichier et le nom
        file_size = os.path.getsize(image_path)
        filename = os.path.basename(image_path).lower()

        # Logique de simulation simple
        confidence = min(85.0, (file_size / 1024) % 100)  # Entre 0 et 85%
        is_ai_generated = 'ai' in filename or 'generated' in filename or confidence > 70

        return {
            "is_ai_generated": is_ai_generated,
            "confidence": confidence,
            "model_used": "Simulation (TensorFlow non disponible)",
            "simulation": True,
            "warning": "Résultats simulés - TensorFlow non installé"
        }

    def is_available(self) -> Dict[str, Any]:
        """
        Vérifie la disponibilité des modèles.

        Returns:
            Dictionnaire indiquant quels modèles sont disponibles
        """
        return {
            "tensorflow_available": TENSORFLOW_AVAILABLE,
            "ai_detection": self.ai_model is not None,
            "resnet50": self.resnet_model is not None,
            "tensorflow_version": tf.__version__ if TENSORFLOW_AVAILABLE else None
        }

    def is_model_loaded(self) -> bool:
        """
        Vérifie si le modèle IA est chargé et disponible.

        Returns:
            True si le modèle est disponible, False sinon
        """
        return TENSORFLOW_AVAILABLE and (self.ai_model is not None or self.resnet_model is not None)
