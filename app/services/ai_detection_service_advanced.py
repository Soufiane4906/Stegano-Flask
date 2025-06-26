"""
Service de détection IA amélioré utilisant des modèles pré-entraînés.
Compatible avec plusieurs types de modèles et méthodes de détection.
"""

import os
import logging
import numpy as np
from PIL import Image
from typing import Dict, Any, Optional
import tensorflow as tf
from tensorflow import keras

logger = logging.getLogger(__name__)

class AIDetectionServiceAdvanced:
    """Service avancé pour la détection d'images générées par IA."""

    def __init__(self, model_path: str = "model.h5"):
        """
        Initialise le service de détection IA.

        Args:
            model_path: Chemin vers le modèle à charger
        """
        self.model_path = model_path
        self.model = None
        self.model_type = None
        self.is_loaded = False

        # Tenter de charger le modèle
        self._load_model()

    def _load_model(self):
        """Charge le modèle IA."""
        try:
            if os.path.exists(self.model_path):
                self.model = keras.models.load_model(self.model_path)
                self.model_type = "custom"
                self.is_loaded = True
                logger.info(f"✅ Modèle personnalisé chargé: {self.model_path}")
            else:
                # Charger un modèle de fallback basé sur MobileNetV2
                self._load_fallback_model()
        except Exception as e:
            logger.warning(f"⚠️ Impossible de charger le modèle {self.model_path}: {e}")
            # Tenter de charger un modèle de fallback
            self._load_fallback_model()

    def _load_fallback_model(self):
        """Charge un modèle de fallback basé sur des caractéristiques pré-entraînées."""
        try:
            logger.info("🔄 Chargement du modèle de fallback...")

            # Créer un modèle simple basé sur MobileNetV2
            base_model = keras.applications.MobileNetV2(
                input_shape=(128, 128, 3),
                include_top=False,
                weights='imagenet'
            )
            base_model.trainable = False

            self.model = keras.Sequential([
                base_model,
                keras.layers.GlobalAveragePooling2D(),
                keras.layers.Dense(128, activation='relu'),
                keras.layers.Dropout(0.5),
                keras.layers.Dense(1, activation='sigmoid')
            ])

            # Compiler le modèle
            self.model.compile(
                optimizer='adam',
                loss='binary_crossentropy',
                metrics=['accuracy']
            )

            self.model_type = "fallback_mobilenet"
            self.is_loaded = True
            logger.info("✅ Modèle de fallback MobileNetV2 chargé")

        except Exception as e:
            logger.error(f"❌ Impossible de charger le modèle de fallback: {e}")
            self.model = None
            self.is_loaded = False

    def detect_ai_image(self, image_path: str) -> Dict[str, Any]:
        """
        Détecte si une image est générée par IA (implémentation exacte de steganoV2.py).

        Args:
            image_path: Chemin vers l'image à analyser

        Returns:
            Dict contenant les résultats de la détection
        """
        try:
            if not self.is_loaded:
                return {
                    "error": "Modèle IA non disponible",
                    "is_ai_generated": False,
                    "confidence": 0.0,
                    "method": "unavailable"
                }

            # Préprocesser l'image exactement comme dans steganoV2.py
            img = Image.open(image_path).convert("RGB")
            img = img.resize((128, 128), Image.Resampling.LANCZOS)
            img_array = np.array(img, dtype=np.float32) / 255.0
            img_array = np.expand_dims(img_array, axis=0)

            # Prédiction
            if self.model_type == "fallback_mobilenet":
                # Pour le modèle de fallback, utiliser une heuristique basée sur les caractéristiques
                prediction = self._fallback_prediction(img_array)
            else:
                # Utiliser le modèle personnalisé
                prediction = self.model.predict(img_array, verbose=0)

            confidence = float(prediction[0][0])
            is_ai_generated = confidence > 0.5

            result = {
                "is_ai_generated": is_ai_generated,
                "confidence": round(confidence * 100, 2),
                "method": self.model_type,
                "model_path": self.model_path if self.model_type == "custom" else "fallback"
            }

            logger.info(f"Détection IA: {confidence*100:.1f}% (méthode: {self.model_type})")
            return result

        except Exception as e:
            logger.error(f"Erreur lors de la détection IA: {str(e)}")
            return {
                "error": f"Erreur lors de la détection: {str(e)}",
                "is_ai_generated": False,
                "confidence": 0.0,
                "method": "error"
            }

    def _fallback_prediction(self, img_array: np.ndarray) -> np.ndarray:
        """
        Prédiction de fallback basée sur des caractéristiques visuelles.

        Args:
            img_array: Image préprocessée

        Returns:
            Prédiction sous forme de tableau numpy
        """
        try:
            # Extraire des caractéristiques avec le modèle de base
            features = self.model.layers[0](img_array)  # MobileNetV2 base
            features = self.model.layers[1](features)   # GlobalAveragePooling2D

            # Analyse heuristique basée sur les caractéristiques
            feature_mean = np.mean(features.numpy())
            feature_std = np.std(features.numpy())

            # Heuristique simple: les images IA ont souvent des patterns spécifiques
            # Cette heuristique peut être améliorée avec plus de recherche
            ai_score = 0.3  # Score de base

            # Ajuster selon les caractéristiques
            if feature_std < 0.1:  # Peu de variation -> potentiellement IA
                ai_score += 0.2
            if feature_mean > 0.8:  # Valeurs élevées -> potentiellement IA
                ai_score += 0.1

            # Limiter entre 0 et 1
            ai_score = max(0.0, min(1.0, ai_score))

            return np.array([[ai_score]])

        except Exception as e:
            logger.error(f"Erreur prédiction fallback: {e}")
            return np.array([[0.3]])  # Score neutre

    def is_available(self) -> Dict[str, Any]:
        """
        Vérifie si le service est disponible.

        Returns:
            Dict avec le statut du service
        """
        return {
            "available": self.is_loaded,
            "model_type": self.model_type,
            "model_path": self.model_path if self.model_type == "custom" else "fallback",
            "tensorflow_version": tf.__version__
        }

    def is_model_loaded(self) -> bool:
        """Vérifie si le modèle est chargé."""
        return self.is_loaded
