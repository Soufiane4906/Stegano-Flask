import os
import uuid
import numpy as np
import cv2
from typing import Optional, Dict, Any, List, Tuple
from PIL import Image
import imagehash
from scipy.spatial.distance import hamming
from app.models.image_models import ImageAnalysis, db
from app.utils.exceptions import SteganographyError
import logging

logger = logging.getLogger(__name__)

class AdvancedSteganographyService:
    """Service avancé pour la stéganographie avec LSB personnalisé et détection de similarité."""

    def __init__(self):
        self.similarity_threshold = 0.85  # 85% de similarité

    def embed_lsb_custom(self, image_path: str, message: str, output_path: str = None) -> Dict[str, Any]:
        """
        Implémentation personnalisée de LSB pour cacher un message dans une image.

        Args:
            image_path: Chemin vers l'image source
            message: Message à cacher
            output_path: Chemin de sortie (optionnel)

        Returns:
            Dict avec les informations sur l'opération
        """
        try:
            # Charger l'image
            img = cv2.imread(image_path)
            if img is None:
                raise SteganographyError(f"Impossible de charger l'image: {image_path}")

            # Convertir le message en binaire
            binary_message = ''.join(format(ord(char), '08b') for char in message)
            binary_message += '1111111111111110'  # Marqueur de fin

            # Vérifier si l'image peut contenir le message
            max_capacity = img.shape[0] * img.shape[1] * 3  # 3 canaux de couleur
            if len(binary_message) > max_capacity:
                raise SteganographyError("Le message est trop long pour cette image")

            # Cacher le message dans les LSB
            img_flat = img.flatten()
            for i, bit in enumerate(binary_message):
                img_flat[i] = (img_flat[i] & 0xFE) | int(bit)

            # Reconstituer l'image
            stego_img = img_flat.reshape(img.shape)

            # Sauvegarder
            if output_path is None:
                base_name = os.path.splitext(os.path.basename(image_path))[0]
                output_path = f"uploads/{base_name}_stego_{uuid.uuid4().hex[:8]}.png"

            cv2.imwrite(output_path, stego_img)

            logger.info(f"Message caché avec succès dans {output_path}")

            return {
                "success": True,
                "output_path": output_path,
                "message_length": len(message),
                "capacity_used": len(binary_message) / max_capacity * 100,
                "method": "LSB_Custom"
            }

        except Exception as e:
            logger.error(f"Erreur LSB custom: {str(e)}")
            raise SteganographyError(f"Erreur lors de l'insertion LSB: {str(e)}")

    def extract_lsb_custom(self, image_path: str) -> Dict[str, Any]:
        """
        Extraction personnalisée de message LSB.

        Args:
            image_path: Chemin vers l'image stéganographiée

        Returns:
            Dict avec le message extrait
        """
        try:
            # Charger l'image
            img = cv2.imread(image_path)
            if img is None:
                raise SteganographyError(f"Impossible de charger l'image: {image_path}")

            # Extraire les LSB
            img_flat = img.flatten()
            binary_message = ""

            for pixel in img_flat:
                binary_message += str(pixel & 1)

                # Vérifier le marqueur de fin
                if binary_message.endswith('1111111111111110'):
                    binary_message = binary_message[:-16]  # Retirer le marqueur
                    break

            # Convertir en texte
            if len(binary_message) % 8 != 0:
                return {
                    "success": False,
                    "message": None,
                    "error": "Message corrompu ou inexistant"
                }

            message = ""
            for i in range(0, len(binary_message), 8):
                byte = binary_message[i:i+8]
                if len(byte) == 8:
                    char = chr(int(byte, 2))
                    message += char

            logger.info(f"Message extrait de {image_path}: {len(message)} caractères")

            return {
                "success": True,
                "message": message,
                "message_length": len(message),
                "method": "LSB_Custom"
            }

        except Exception as e:
            logger.error(f"Erreur extraction LSB: {str(e)}")
            return {
                "success": False,
                "message": None,
                "error": str(e)
            }

    def generate_image_hashes(self, image_path: str) -> Dict[str, Any]:
        """
        Génère les hashes perceptuels d'une image.

        Args:
            image_path: Chemin vers l'image

        Returns:
            Dict avec les différents hashes
        """
        try:
            img = Image.open(image_path)

            # Générer les hashes perceptuels
            phash = str(imagehash.phash(img))
            dhash = str(imagehash.dhash(img))
            ahash = str(imagehash.average_hash(img))
            whash = str(imagehash.whash(img))

            return {
                "success": True,
                "phash": phash,
                "dhash": dhash,
                "ahash": ahash,
                "whash": whash
            }

        except Exception as e:
            logger.error(f"Erreur génération hashes: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def find_similar_images(self, image_path: str) -> List[Dict[str, Any]]:
        """
        Trouve des images similaires dans la base de données.

        Args:
            image_path: Chemin vers l'image de référence

        Returns:
            Liste des images similaires avec scores
        """
        try:
            # Générer les hashes de l'image de référence
            ref_hashes = self.generate_image_hashes(image_path)
            if not ref_hashes["success"]:
                return []

            # Rechercher dans la base de données
            similar_images = []
            analyses = ImageAnalysis.query.all()

            for analysis in analyses:
                if analysis.metadata and 'hashes' in analysis.metadata:
                    db_hashes = analysis.metadata['hashes']

                    # Calculer la similarité pour chaque type de hash
                    similarities = {}

                    for hash_type in ['phash', 'dhash', 'ahash']:
                        if hash_type in ref_hashes and hash_type in db_hashes:
                            ref_hash_bits = [int(bit) for bit in ref_hashes[hash_type]]
                            db_hash_bits = [int(bit) for bit in db_hashes[hash_type]]

                            if len(ref_hash_bits) == len(db_hash_bits):
                                similarity = 1 - hamming(ref_hash_bits, db_hash_bits)
                                similarities[hash_type] = similarity

                    # Moyenne des similarités
                    if similarities:
                        avg_similarity = sum(similarities.values()) / len(similarities)

                        if avg_similarity >= self.similarity_threshold:
                            similar_images.append({
                                "id": analysis.id,
                                "filename": analysis.metadata.get('filename', 'Inconnu'),
                                "similarity_score": avg_similarity,
                                "similarities": similarities,
                                "timestamp": analysis.created_at.isoformat() if analysis.created_at else None
                            })

            # Trier par score de similarité décroissant
            similar_images.sort(key=lambda x: x["similarity_score"], reverse=True)

            logger.info(f"Trouvé {len(similar_images)} images similaires")
            return similar_images

        except Exception as e:
            logger.error(f"Erreur recherche similarité: {str(e)}")
            return []

    def analyze_image_structure(self, image_path: str) -> Dict[str, Any]:
        """
        Analyse la structure d'une image pour détecter des anomalies.

        Args:
            image_path: Chemin vers l'image

        Returns:
            Dict avec les résultats d'analyse
        """
        try:
            img = cv2.imread(image_path)
            if img is None:
                raise SteganographyError(f"Impossible de charger l'image: {image_path}")

            # Analyse statistique des pixels
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Calcul des statistiques
            mean_pixel = np.mean(gray)
            std_pixel = np.std(gray)

            # Analyse des LSB (test de Chi-carré)
            lsb_plane = gray & 1
            lsb_ratio = np.sum(lsb_plane) / lsb_plane.size

            # Analyse des contours (détection d'artefacts)
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size

            # Score de suspicion (heuristique)
            suspicion_score = 0.0

            # LSB ratio très proche de 0.5 peut indiquer de la stéganographie
            if 0.45 <= lsb_ratio <= 0.55:
                suspicion_score += 0.3

            # Faible variation peut indiquer une modification
            if std_pixel < 30:
                suspicion_score += 0.2

            # Densité de contours anormale
            if edge_density < 0.05 or edge_density > 0.3:
                suspicion_score += 0.2

            return {
                "success": True,
                "statistics": {
                    "mean_pixel": float(mean_pixel),
                    "std_pixel": float(std_pixel),
                    "lsb_ratio": float(lsb_ratio),
                    "edge_density": float(edge_density)
                },
                "suspicion_score": float(suspicion_score),
                "analysis": {
                    "likely_steganography": suspicion_score > 0.5,
                    "confidence": min(suspicion_score * 2, 1.0)
                }
            }

        except Exception as e:
            logger.error(f"Erreur analyse structure: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
