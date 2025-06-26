import os
import hashlib
from typing import Optional, Dict, Any
from stegano import lsb
from PIL import Image
import imagehash
import cv2
import numpy as np
from scipy.spatial.distance import hamming
from app.models.image_models import ImageAnalysis, db
from app.utils.exceptions import SteganographyError
import logging

logger = logging.getLogger(__name__)

class SteganographyService:
    """Service pour gérer les opérations de stéganographie."""

    @staticmethod
    def detect_hidden_message(image_path: str) -> Dict[str, Any]:
        """
        Détecte si une image contient un message caché (implémentation exacte de steganoV2.py).

        Args:
            image_path: Chemin vers l'image à analyser

        Returns:
            Dict contenant les résultats de l'analyse
        """
        try:
            hidden_message = lsb.reveal(image_path)
            return {"signature_detected": True, "signature": hidden_message} if hidden_message else {"signature_detected": False}
        except Exception as e:
            return {"error": "Impossible to detect message."}

    @staticmethod
    def embed_message(image_path: str, message: str, output_path: Optional[str] = None) -> str:
        """
        Cache un message dans une image (implémentation exacte de steganoV2.py).

        Args:
            image_path: Chemin vers l'image source
            message: Message à cacher
            output_path: Chemin de sortie (optionnel)

        Returns:
            Chemin vers l'image avec le message caché
        """
        try:
            if not output_path:
                output_path = image_path.replace(".", "_steg.")

            # Vérifier que l'image source existe
            if not os.path.exists(image_path):
                raise SteganographyError(f"Image source introuvable: {image_path}")

            # Créer l'image avec le message caché (logique exacte de steganoV2.py)
            hidden_image = lsb.hide(image_path, message)
            hidden_image.save(output_path)

            logger.info(f"Message caché avec succès dans {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Erreur lors de l'intégration du message: {str(e)}")
            raise SteganographyError(f"Impossible de cacher le message: {str(e)}")

    @staticmethod
    def generate_image_context_signature(image_path: str) -> str:
        """
        Génère une signature contextuelle pour une image basée sur ses caractéristiques visuelles.

        Args:
            image_path: Chemin vers l'image

        Returns:
            Signature contextuelle de l'image
        """
        try:
            # Charger l'image avec OpenCV
            img = cv2.imread(image_path)
            if img is None:
                raise SteganographyError(f"Impossible de charger l'image: {image_path}")

            # Convertir en niveaux de gris pour simplifier
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Calculer des caractéristiques visuelles
            # 1. Histogramme des niveaux de gris
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            hist_features = hist.flatten()[:50]  # Prendre les 50 premières valeurs

            # 2. Moments de Hu (invariants géométriques)
            moments = cv2.moments(gray)
            hu_moments = cv2.HuMoments(moments).flatten()

            # 3. Statistiques de base
            mean_val = np.mean(gray)
            std_val = np.std(gray)

            # Combiner toutes les caractéristiques
            features = np.concatenate([
                hist_features,
                hu_moments,
                [mean_val, std_val]
            ])

            # Créer une signature basée sur ces caractéristiques
            feature_hash = hashlib.sha256(features.tobytes()).hexdigest()

            return f"CV:{feature_hash[:32]}"

        except Exception as e:
            logger.error(f"Erreur lors de la génération de signature contextuelle: {str(e)}")
            raise SteganographyError(f"Erreur lors de la génération de signature contextuelle: {str(e)}")

    @staticmethod
    def generate_image_hashes(image_path: str) -> Dict[str, str]:
        """
        Génère plusieurs types de hashes pour une image.

        Args:
            image_path: Chemin vers l'image

        Returns:
            Dictionnaire contenant les différents hashes
        """
        try:
            img = Image.open(image_path)

            # Générer perceptual hash (pHash)
            phash = str(imagehash.phash(img))

            # Générer difference hash (dHash)
            dhash = str(imagehash.dhash(img))

            return {
                "phash": phash,
                "dhash": dhash
            }
        except Exception as e:
            logger.error(f"Erreur lors de la génération des hashes: {str(e)}")
            raise SteganographyError(f"Erreur lors de la génération des hashes: {str(e)}")

    @staticmethod
    def find_similar_images_advanced(hashes: Dict[str, str], threshold: float = 0.85) -> list:
        """
        Trouve des images similaires en utilisant plusieurs méthodes de hash.

        Args:
            hashes: Dictionnaire contenant les hashes de l'image
            threshold: Seuil de similitude (0-1)

        Returns:
            Liste des images similaires
        """
        try:
            similar_images = []

            # Récupérer toutes les images de la base de données
            all_images = ImageAnalysis.query.filter(
                ImageAnalysis.perceptual_hash.isnot(None)
            ).all()

            for img in all_images:
                try:
                    # Calculer la distance de Hamming pour pHash
                    phash_similarity = 1 - hamming(
                        [int(bit) for bit in hashes["phash"]],
                        [int(bit) for bit in img.perceptual_hash]
                    )

                    # Calculer la distance de Hamming pour dHash si disponible
                    dhash_similarity = 0.5  # Valeur par défaut
                    if hasattr(img, 'dhash') and img.dhash:
                        dhash_similarity = 1 - hamming(
                            [int(bit) for bit in hashes["dhash"]],
                            [int(bit) for bit in img.dhash]
                        )

                    # Moyenne des similitudes
                    avg_similarity = (phash_similarity + dhash_similarity) / 2

                    if avg_similarity >= threshold:
                        similar_images.append({
                            "id": img.id,
                            "filename": img.filename,
                            "image_path": img.image_path,
                            "similarity": avg_similarity * 100  # Convertir en pourcentage
                        })
                except Exception as e:
                    logger.warning(f"Erreur lors de la comparaison avec l'image {img.id}: {str(e)}")
                    continue

            return sorted(similar_images, key=lambda x: x['similarity'], reverse=True)

        except Exception as e:
            logger.error(f"Erreur lors de la recherche d'images similaires: {str(e)}")
            return []

    @staticmethod
    def calculate_perceptual_hash(image_path: str) -> str:
        """
        Calcule le hash perceptuel d'une image pour la détection de similitude.

        Args:
            image_path: Chemin vers l'image

        Returns:
            Hash perceptuel sous forme de string
        """
        try:
            with Image.open(image_path) as img:
                # Utiliser pHash pour la détection de similitude
                phash = imagehash.phash(img)
                return str(phash)

        except Exception as e:
            logger.error(f"Erreur lors du calcul du hash perceptuel: {str(e)}")
            raise SteganographyError(f"Impossible de calculer le hash: {str(e)}")

    @staticmethod
    def calculate_md5_hash(image_path: str) -> str:
        """
        Calcule le hash MD5 d'une image pour la détection de duplicatas exacts.

        Args:
            image_path: Chemin vers l'image

        Returns:
            Hash MD5 sous forme de string
        """
        try:
            with open(image_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()

        except Exception as e:
            logger.error(f"Erreur lors du calcul du hash MD5: {str(e)}")
            raise SteganographyError(f"Impossible de calculer le hash MD5: {str(e)}")

    @staticmethod
    def find_similar_images(image_path: str, threshold: float = 0.85) -> list:
        """
        Trouve des images similaires dans la base de données.

        Args:
            image_path: Chemin vers l'image à comparer
            threshold: Seuil de similitude (0-1)

        Returns:
            Liste des images similaires
        """
        try:
            current_hash = SteganographyService.calculate_perceptual_hash(image_path)
            current_hash_bin = bin(int(current_hash, 16))[2:].zfill(64)

            similar_images = []
            all_images = ImageAnalysis.query.filter(
                ImageAnalysis.perceptual_hash.isnot(None)
            ).all()

            for img in all_images:
                if img.perceptual_hash:
                    stored_hash_bin = bin(int(img.perceptual_hash, 16))[2:].zfill(64)

                    # Calculer la distance de Hamming
                    hamming_distance = sum(c1 != c2 for c1, c2 in zip(current_hash_bin, stored_hash_bin))
                    similarity = 1 - (hamming_distance / 64)

                    if similarity >= threshold:
                        similar_images.append({
                            'image': img,
                            'similarity': similarity
                        })

            return sorted(similar_images, key=lambda x: x['similarity'], reverse=True)

        except Exception as e:
            logger.error(f"Erreur lors de la recherche d'images similaires: {str(e)}")
            return []
