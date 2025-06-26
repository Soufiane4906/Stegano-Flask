import os
import uuid
from typing import Dict, Any, Optional, Tuple
from PIL import Image
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import logging
import imagehash
from scipy.spatial.distance import hamming
from app.models.image_models import ImageAnalysis, db
from app.services.steganography_service import SteganographyService
from app.services.ai_detection_service_v2 import AIDetectionService
from app.utils.exceptions import ImageProcessingError
from datetime import datetime

logger = logging.getLogger(__name__)

class ImageService:
    """Service pour gérer les opérations sur les images."""

    def __init__(self, upload_folder: str, ai_service: AIDetectionService):
        """
        Initialise le service d'images.

        Args:
            upload_folder: Dossier de téléchargement
            ai_service: Service de détection IA
        """
        self.upload_folder = upload_folder
        self.ai_service = ai_service
        self.steganography_service = SteganographyService()

        # Créer le dossier s'il n'existe pas
        os.makedirs(upload_folder, exist_ok=True)

    def process_uploaded_image(self, file: FileStorage, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Traite une image téléchargée complètement.

        Args:
            file: Fichier téléchargé
            user_id: ID de l'utilisateur (optionnel)

        Returns:
            Dictionnaire avec tous les résultats d'analyse
        """
        try:
            # Sauvegarder le fichier
            filename, filepath = self._save_uploaded_file(file)

            # Extraire les métadonnées
            metadata = self._extract_metadata(filepath)

            # Analyser la stéganographie
            steg_result = self.steganography_service.detect_hidden_message(filepath)

            # Détecter si l'image est générée par IA
            ai_result = {}
            if self.ai_service.is_model_loaded():
                ai_result = self.ai_service.detect_ai_image(filepath)
            else:
                ai_result = {"error": "Modèle IA non disponible"}

            # Calculer les hashs
            perceptual_hash = self.steganography_service.calculate_perceptual_hash(filepath)
            md5_hash = self.steganography_service.calculate_md5_hash(filepath)

            # Chercher des images similaires
            similar_images = self.steganography_service.find_similar_images(filepath)

            # Créer l'enregistrement en base
            image_analysis = self._create_image_record(
                filename=filename,
                original_filename=file.filename,
                filepath=filepath,
                metadata=metadata,
                steg_result=steg_result,
                ai_result=ai_result,
                perceptual_hash=perceptual_hash,
                md5_hash=md5_hash,
                user_id=user_id
            )

            # Résultat complet
            result = {
                "id": image_analysis.id,
                "filename": filename,
                "image_path": filepath,
                "metadata": metadata,
                "steganography": steg_result,
                "ai_detection": ai_result,
                "similar_images": [
                    {
                        "id": sim["image"].id,
                        "filename": sim["image"].filename,
                        "similarity": sim["similarity"]
                    } for sim in similar_images[:5]  # Limiter à 5 résultats
                ],
                "hashes": {
                    "perceptual": perceptual_hash,
                    "md5": md5_hash
                }
            }

            logger.info(f"Image traitée avec succès: {filename}")
            return result

        except Exception as e:
            logger.error(f"Erreur lors du traitement de l'image: {str(e)}")
            raise ImageProcessingError(f"Impossible de traiter l'image: {str(e)}")

    def add_steganography_to_image(self, file: FileStorage, message: str) -> Dict[str, Any]:
        """
        Ajoute un message caché à une image.

        Args:
            file: Fichier image
            message: Message à cacher

        Returns:
            Informations sur l'image avec le message caché
        """
        try:
            # Sauvegarder le fichier original
            filename, filepath = self._save_uploaded_file(file)

            # Créer l'image avec le message caché
            steg_filepath = self.steganography_service.embed_message(filepath, message)
            steg_filename = os.path.basename(steg_filepath)

            # URL publique pour l'image avec stéganographie
            public_url = f"/uploads/{steg_filename}"

            result = {
                "message": "Message caché ajouté avec succès",
                "original_image": filename,
                "steganography_image": steg_filename,
                "image_url": public_url,
                "hidden_message": message
            }

            logger.info(f"Stéganographie ajoutée: {steg_filename}")
            return result

        except Exception as e:
            logger.error(f"Erreur lors de l'ajout de stéganographie: {str(e)}")
            raise ImageProcessingError(f"Impossible d'ajouter le message caché: {str(e)}")

    def _save_uploaded_file(self, file: FileStorage) -> Tuple[str, str]:
        """
        Sauvegarde un fichier téléchargé de manière sécurisée.

        Args:
            file: Fichier à sauvegarder

        Returns:
            Tuple (nom_fichier, chemin_complet)
        """
        # Générer un nom unique
        filename = str(uuid.uuid4()) + os.path.splitext(secure_filename(file.filename or ''))[1]
        filepath = os.path.join(self.upload_folder, filename)

        # Sauvegarder le fichier
        file.save(filepath)

        return filename, filepath

    def _extract_metadata(self, image_path: str) -> Dict[str, Any]:
        """
        Extrait les métadonnées d'une image.

        Args:
            image_path: Chemin vers l'image

        Returns:
            Dictionnaire des métadonnées
        """
        try:
            with Image.open(image_path) as img:
                file_size = os.path.getsize(image_path)

                return {
                    "dimensions": f"{img.width}x{img.height}",
                    "width": img.width,
                    "height": img.height,
                    "format": img.format,
                    "mode": img.mode,
                    "size": f"{file_size / 1024:.2f} KB",
                    "size_bytes": file_size
                }
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des métadonnées: {str(e)}")
            return {"error": str(e)}

    def _create_image_record(self, **kwargs) -> ImageAnalysis:
        """
        Crée un enregistrement d'analyse d'image en base.

        Returns:
            Instance ImageAnalysis créée
        """
        try:
            analysis = ImageAnalysis(
                filename=kwargs['filename'],
                original_filename=kwargs['original_filename'],
                file_path=kwargs['filepath'],
                file_size=kwargs['metadata'].get('size_bytes'),
                width=kwargs['metadata'].get('width'),
                height=kwargs['metadata'].get('height'),
                format=kwargs['metadata'].get('format'),
                has_steganography=kwargs['steg_result'].get('signature_detected', False),
                steganography_message=kwargs['steg_result'].get('signature'),
                is_ai_generated=kwargs['ai_result'].get('is_ai_generated'),
                ai_confidence=kwargs['ai_result'].get('confidence'),
                perceptual_hash=kwargs['perceptual_hash'],
                md5_hash=kwargs['md5_hash'],
                user_id=kwargs.get('user_id'),
                analyzed_at=datetime.utcnow()
            )

            db.session.add(analysis)
            db.session.commit()

            return analysis

        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la création de l'enregistrement: {str(e)}")
            raise ImageProcessingError(f"Impossible de sauvegarder l'analyse: {str(e)}")

    def get_analysis_history(self, user_id: Optional[int] = None, limit: int = 50) -> list:
        """
        Récupère l'historique des analyses.

        Args:
            user_id: ID utilisateur (None pour tous)
            limit: Nombre maximum de résultats

        Returns:
            Liste des analyses
        """
        query = ImageAnalysis.query

        if user_id:
            query = query.filter_by(user_id=user_id)

        analyses = query.order_by(ImageAnalysis.created_at.desc()).limit(limit).all()

        return [analysis.to_dict() for analysis in analyses]

    def compare_similarity(self, file1: FileStorage, file2: FileStorage) -> Dict[str, Any]:
        """
        Compare la similarité entre deux images (implémentation exacte de steganoV2.py).

        Args:
            file1: Premier fichier image
            file2: Deuxième fichier image

        Returns:
            Dictionnaire avec les résultats de comparaison
        """
        try:
            from scipy.spatial.distance import hamming

            # Sauvegarder temporairement les fichiers
            filename1, filepath1 = self._save_uploaded_file(file1)
            filename2, filepath2 = self._save_uploaded_file(file2)

            # Générer les hashes comme dans steganoV2.py
            def generate_image_hashes_local(image_path):
                try:
                    img = Image.open(image_path)
                    # Generate perceptual hash (pHash)
                    phash = str(imagehash.phash(img))
                    # Generate difference hash (dHash)
                    dhash = str(imagehash.dhash(img))
                    return {"phash": phash, "dhash": dhash}
                except Exception as e:
                    return {"error": f"Failed to generate hashes: {str(e)}"}

            # Générer les hashes pour les deux images
            hashes1 = generate_image_hashes_local(filepath1)
            hashes2 = generate_image_hashes_local(filepath2)

            if "error" in hashes1 or "error" in hashes2:
                raise ImageProcessingError("Erreur lors de la génération des hashes")

            # Calculer la similarité comme dans steganoV2.py
            # Convertir les hashes hexadécimaux en chaînes binaires
            def hex_to_binary(hex_string):
                """Convertit un hash hexadécimal en chaîne binaire."""
                return bin(int(hex_string, 16))[2:].zfill(len(hex_string) * 4)

            # Convertir en binaire pour le calcul de Hamming
            phash1_binary = hex_to_binary(hashes1["phash"])
            phash2_binary = hex_to_binary(hashes2["phash"])
            dhash1_binary = hex_to_binary(hashes1["dhash"])
            dhash2_binary = hex_to_binary(hashes2["dhash"])

            # Calculer la distance de Hamming
            phash_similarity = 1 - hamming(
                [int(bit) for bit in phash1_binary],
                [int(bit) for bit in phash2_binary]
            )

            dhash_similarity = 1 - hamming(
                [int(bit) for bit in dhash1_binary],
                [int(bit) for bit in dhash2_binary]
            )

            # Convertir en types Python natifs pour éviter les erreurs JSON
            phash_similarity = float(phash_similarity)
            dhash_similarity = float(dhash_similarity)

            # Average the similarities
            avg_similarity = (phash_similarity + dhash_similarity) / 2
            avg_similarity_percent = avg_similarity * 100  # Convert to percentage

            result = {
                "status": "success",
                "files": {
                    "file1": filename1,
                    "file2": filename2
                },
                "similarity": {
                    "phash": round(phash_similarity * 100, 2),
                    "dhash": round(dhash_similarity * 100, 2),
                    "average": round(avg_similarity_percent, 2)
                },
                "hashes": {
                    "file1": hashes1,
                    "file2": hashes2
                },
                "method": "steganoV2_hamming_distance",
                "identical": bool(avg_similarity_percent > 95),  # Conversion explicite en bool
                "similar": bool(avg_similarity_percent >= 85),   # Conversion explicite en bool
                "timestamp": datetime.utcnow().isoformat()
            }

            logger.info(f"Comparaison de similarité effectuée (steganoV2): {avg_similarity_percent:.2f}%")
            return result

        except Exception as e:
            logger.error(f"Erreur lors de la comparaison de similarité: {str(e)}")
            raise ImageProcessingError(f"Erreur lors de la comparaison: {str(e)}")
