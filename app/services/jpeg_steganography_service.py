"""
Service de stéganographie spécialisé pour les images JPEG.
Utilise les techniques spécifiques au format JPEG comme :
- Modification des coefficients DCT
- Injection dans les segments EXIF
- Manipulation des tables de quantification
"""

import os
import io
import numpy as np
from PIL import Image, ExifTags
from PIL.ExifTags import TAGS
import hashlib
import base64
import struct
import logging
from typing import Dict, Any, Optional, Tuple, Union
import json

logger = logging.getLogger(__name__)

class JPEGSteganographyService:
    """Service de stéganographie pour images JPEG."""

    def __init__(self):
        """Initialise le service de stéganographie JPEG."""
        self.supported_formats = ['JPEG', 'JPG']
        self.max_message_length = 1024 * 1024  # 1MB max

    def hide_message_in_jpeg(self, image_path: str, message: str, output_path: str = None,
                           method: str = 'exif') -> Dict[str, Any]:
        """
        Cache un message dans une image JPEG.

        Args:
            image_path: Chemin vers l'image JPEG source
            message: Message à cacher
            output_path: Chemin de sortie (optionnel)
            method: Méthode de stéganographie ('exif', 'dct', 'lsb')

        Returns:
            Dictionnaire avec les informations sur l'opération
        """
        try:
            # Vérifier que le fichier est un JPEG
            if not self._is_jpeg(image_path):
                raise ValueError("Le fichier n'est pas une image JPEG valide")

            # Vérifier la taille du message
            if len(message.encode('utf-8')) > self.max_message_length:
                raise ValueError(f"Message trop long (max: {self.max_message_length} bytes)")

            # Générer le chemin de sortie si non spécifié
            if output_path is None:
                base, ext = os.path.splitext(image_path)
                output_path = f"{base}_stego{ext}"

            # Appliquer la méthode de stéganographie choisie
            if method == 'exif':
                result = self._hide_in_exif(image_path, message, output_path)
            elif method == 'lsb':
                result = self._hide_in_lsb_jpeg(image_path, message, output_path)
            elif method == 'dct':
                result = self._hide_in_dct(image_path, message, output_path)
            else:
                raise ValueError(f"Méthode non supportée: {method}")

            result.update({
                'input_path': image_path,
                'output_path': output_path,
                'method': method,
                'message_length': len(message),
                'success': True
            })

            logger.info(f"Message caché avec succès dans {output_path} (méthode: {method})")
            return result

        except Exception as e:
            logger.error(f"Erreur lors de la dissimulation: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'input_path': image_path,
                'method': method
            }

    def extract_message_from_jpeg(self, image_path: str, method: str = 'exif') -> Dict[str, Any]:
        """
        Extrait un message caché d'une image JPEG.

        Args:
            image_path: Chemin vers l'image JPEG
            method: Méthode d'extraction ('exif', 'dct', 'lsb')

        Returns:
            Dictionnaire avec le message extrait et les informations
        """
        try:
            # Vérifier que le fichier est un JPEG
            if not self._is_jpeg(image_path):
                raise ValueError("Le fichier n'est pas une image JPEG valide")

            # Appliquer la méthode d'extraction choisie
            if method == 'exif':
                result = self._extract_from_exif(image_path)
            elif method == 'lsb':
                result = self._extract_from_lsb_jpeg(image_path)
            elif method == 'dct':
                result = self._extract_from_dct(image_path)
            else:
                raise ValueError(f"Méthode non supportée: {method}")

            result.update({
                'image_path': image_path,
                'method': method,
                'success': True
            })

            if result.get('message'):
                logger.info(f"Message extrait avec succès de {image_path} (méthode: {method})")
            else:
                logger.info(f"Aucun message trouvé dans {image_path} (méthode: {method})")

            return result

        except Exception as e:
            logger.error(f"Erreur lors de l'extraction: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'image_path': image_path,
                'method': method
            }

    def _hide_in_exif(self, image_path: str, message: str, output_path: str) -> Dict[str, Any]:
        """Cache un message dans les données EXIF."""
        try:
            import piexif
            
            # Encoder le message en base64
            encoded_message = base64.b64encode(message.encode('utf-8')).decode('ascii')

            # Charger l'image
            img = Image.open(image_path)

            # Obtenir les données EXIF existantes ou créer un dictionnaire vide
            try:
                exif_dict = piexif.load(image_path)
            except:
                # Si pas d'EXIF existant, créer une structure vide
                exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}

            # Ajouter notre message dans le champ UserComment
            # Le UserComment doit commencer par un code de caractères (8 bytes)
            user_comment = b"ASCII\x00\x00\x00" + encoded_message.encode('ascii')
            exif_dict["Exif"][piexif.ExifIFD.UserComment] = user_comment

            # Convertir en bytes pour PIL
            exif_bytes = piexif.dump(exif_dict)

            # Sauvegarder l'image avec les nouvelles données EXIF
            img.save(output_path, "JPEG", exif=exif_bytes, quality=95)

            return {
                'exif_tag_used': 'UserComment',
                'encoded_length': len(encoded_message),
                'original_size': os.path.getsize(image_path),
                'modified_size': os.path.getsize(output_path)
            }

        except Exception as e:
            raise Exception(f"Erreur EXIF: {str(e)}")

    def _extract_from_exif(self, image_path: str) -> Dict[str, Any]:
        """Extrait un message des données EXIF."""
        try:
            import piexif
            
            # Charger les données EXIF
            try:
                exif_dict = piexif.load(image_path)
            except:
                return {'message': None, 'info': 'Aucune donnée EXIF trouvée'}

            # Chercher notre message dans le UserComment
            if "Exif" in exif_dict and piexif.ExifIFD.UserComment in exif_dict["Exif"]:
                user_comment = exif_dict["Exif"][piexif.ExifIFD.UserComment]
                
                if isinstance(user_comment, bytes) and len(user_comment) > 8:
                    # Enlever les 8 premiers bytes (code de caractères)
                    encoded_message = user_comment[8:].decode('ascii')
                    
                    try:
                        # Décoder le message
                        message = base64.b64decode(encoded_message).decode('utf-8')
                        return {
                            'message': message,
                            'exif_tag_used': 'UserComment',
                            'encoded_length': len(encoded_message)
                        }
                    except Exception:
                        pass

            return {'message': None, 'info': 'Aucun message trouvé dans EXIF'}

        except Exception as e:
            raise Exception(f"Erreur extraction EXIF: {str(e)}")

    def _hide_in_lsb_jpeg(self, image_path: str, message: str, output_path: str) -> Dict[str, Any]:
        """Cache un message en utilisant LSB sur l'image JPEG décompressée."""
        try:
            # Charger l'image
            img = Image.open(image_path)
            img = img.convert('RGB')

            # Convertir en array numpy
            img_array = np.array(img)

            # Préparer le message avec un délimiteur
            message_with_delimiter = message + "<<<END_OF_MESSAGE>>>"
            message_bytes = message_with_delimiter.encode('utf-8')

            # Convertir en bits
            message_bits = ''.join([format(byte, '08b') for byte in message_bytes])

            # Vérifier qu'on a assez de place
            total_pixels = img_array.shape[0] * img_array.shape[1] * img_array.shape[2]
            if len(message_bits) > total_pixels:
                raise ValueError("Message trop long pour cette image")

            # Modifier les LSB
            flat_array = img_array.flatten()
            for i, bit in enumerate(message_bits):
                flat_array[i] = (flat_array[i] & 0xFE) | int(bit)

            # Reconstruire l'image
            modified_array = flat_array.reshape(img_array.shape)
            modified_img = Image.fromarray(modified_array.astype(np.uint8))

            # Sauvegarder
            modified_img.save(output_path, "JPEG", quality=95)

            return {
                'pixels_modified': len(message_bits),
                'total_pixels': total_pixels,
                'compression_ratio': len(message_bits) / total_pixels
            }

        except Exception as e:
            raise Exception(f"Erreur LSB JPEG: {str(e)}")

    def _extract_from_lsb_jpeg(self, image_path: str) -> Dict[str, Any]:
        """Extrait un message en utilisant LSB sur l'image JPEG."""
        try:
            # Charger l'image
            img = Image.open(image_path)
            img = img.convert('RGB')
            img_array = np.array(img)

            # Extraire les LSB
            flat_array = img_array.flatten()
            binary_message = ''

            # Chercher le délimiteur
            delimiter = "<<<END_OF_MESSAGE>>>"
            delimiter_binary = ''.join([format(byte, '08b') for byte in delimiter.encode('utf-8')])

            # Extraire bit par bit jusqu'à trouver le délimiteur
            for i in range(len(flat_array)):
                binary_message += str(flat_array[i] & 1)

                # Vérifier si on a assez de bits pour former un caractère
                if len(binary_message) % 8 == 0 and len(binary_message) >= len(delimiter_binary):
                    # Convertir en texte et chercher le délimiteur
                    try:
                        bytes_data = []
                        for j in range(0, len(binary_message), 8):
                            byte_str = binary_message[j:j+8]
                            bytes_data.append(int(byte_str, 2))

                        text = bytes(bytes_data).decode('utf-8', errors='ignore')
                        if delimiter in text:
                            message = text.split(delimiter)[0]
                            return {
                                'message': message,
                                'bits_extracted': len(binary_message),
                                'method_details': 'LSB extraction with delimiter'
                            }
                    except:
                        continue

            return {'message': None, 'info': 'Aucun message trouvé avec LSB'}

        except Exception as e:
            raise Exception(f"Erreur extraction LSB: {str(e)}")

    def _hide_in_dct(self, image_path: str, message: str, output_path: str) -> Dict[str, Any]:
        """Cache un message en modifiant les coefficients DCT (technique avancée)."""
        try:
            # Note: Cette implémentation est simplifiée
            # Une vraie implémentation DCT nécessiterait des bibliothèques spécialisées

            # Pour l'instant, utilisons une approche hybride
            logger.warning("Méthode DCT simplifiée - utilisation de LSB comme fallback")
            return self._hide_in_lsb_jpeg(image_path, message, output_path)

        except Exception as e:
            raise Exception(f"Erreur DCT: {str(e)}")

    def _extract_from_dct(self, image_path: str) -> Dict[str, Any]:
        """Extrait un message des coefficients DCT."""
        try:
            # Fallback vers LSB pour cette implémentation simplifiée
            logger.warning("Méthode DCT simplifiée - utilisation de LSB comme fallback")
            return self._extract_from_lsb_jpeg(image_path)

        except Exception as e:
            raise Exception(f"Erreur extraction DCT: {str(e)}")

    def _is_jpeg(self, image_path: str) -> bool:
        """Vérifie si le fichier est une image JPEG valide."""
        try:
            with Image.open(image_path) as img:
                return img.format in ['JPEG', 'JPG']
        except:
            return False

    def analyze_jpeg_capacity(self, image_path: str) -> Dict[str, Any]:
        """Analyse la capacité de dissimulation d'une image JPEG."""
        try:
            if not self._is_jpeg(image_path):
                raise ValueError("Le fichier n'est pas une image JPEG valide")

            img = Image.open(image_path)
            width, height = img.size

            # Calculer les capacités pour chaque méthode
            lsb_capacity = (width * height * 3) // 8  # bits -> bytes
            exif_capacity = 32768  # Limitation typique des champs EXIF

            # Analyser les données EXIF existantes
            exif_info = {}
            if hasattr(img, '_getexif') and img._getexif() is not None:
                exif_data = img._getexif()
                exif_info = {
                    'tags_count': len(exif_data),
                    'has_usercomment': 0x9286 in exif_data,
                    'existing_tags': list(exif_data.keys())[:10]  # Premiers 10 tags
                }

            return {
                'image_info': {
                    'width': width,
                    'height': height,
                    'dimensions': f"{width}x{height}"
                },
                'file_size': os.path.getsize(image_path),
                'lsb_capacity': lsb_capacity,
                'exif_capacity': exif_capacity,
                'capacity_lsb_bytes': lsb_capacity,
                'capacity_exif_bytes': exif_capacity,
                'recommended_method': 'exif' if lsb_capacity > 10000 else 'lsb',
                'exif_analysis': exif_info,
                'quality_estimate': self._estimate_jpeg_quality(image_path)
            }

        except Exception as e:
            logger.error(f"Erreur analyse capacité: {str(e)}")
            return {'error': str(e)}

    def _estimate_jpeg_quality(self, image_path: str) -> int:
        """Estime la qualité JPEG (approximation)."""
        try:
            # Méthode approximative basée sur la taille du fichier
            img = Image.open(image_path)
            width, height = img.size
            file_size = os.path.getsize(image_path)

            # Calcul approximatif de la qualité
            pixels = width * height
            bytes_per_pixel = file_size / pixels

            if bytes_per_pixel > 2:
                return 95
            elif bytes_per_pixel > 1:
                return 80
            elif bytes_per_pixel > 0.5:
                return 60
            else:
                return 40

        except:
            return 75  # Valeur par défaut

    def create_steganographic_signature(self, image_path: str, output_path: str = None) -> Dict[str, Any]:
        """Crée une signature stéganographique unique pour l'image."""
        try:
            # Générer une signature basée sur le contenu de l'image
            img = Image.open(image_path)
            img_array = np.array(img)

            # Créer un hash du contenu
            content_hash = hashlib.md5(img_array.tobytes()).hexdigest()

            # Créer une signature avec timestamp
            signature_data = {
                'content_hash': content_hash,
                'timestamp': int(np.datetime64('now').astype(int)),
                'dimensions': img.size,
                'format': img.format
            }

            signature_message = json.dumps(signature_data)

            # Cacher la signature dans l'image
            if output_path is None:
                base, ext = os.path.splitext(image_path)
                output_path = f"{base}_signed{ext}"

            result = self.hide_message_in_jpeg(
                image_path,
                signature_message,
                output_path,
                method='exif'
            )

            result['signature_data'] = signature_data
            return result

        except Exception as e:
            logger.error(f"Erreur création signature: {str(e)}")
            return {'success': False, 'error': str(e)}

    def verify_steganographic_signature(self, image_path: str) -> Dict[str, Any]:
        """Vérifie l'intégrité d'une signature stéganographique."""
        try:
            # Extraire la signature
            extraction_result = self.extract_message_from_jpeg(image_path, method='exif')

            if not extraction_result.get('message'):
                return {
                    'verified': False,
                    'reason': 'Aucune signature trouvée'
                }

            try:
                signature_data = json.loads(extraction_result['message'])
            except:
                return {
                    'verified': False,
                    'reason': 'Signature invalide ou corrompue'
                }

            # Recalculer le hash du contenu actuel
            img = Image.open(image_path)
            img_array = np.array(img)
            current_hash = hashlib.md5(img_array.tobytes()).hexdigest()

            # Comparer avec la signature
            original_hash = signature_data.get('content_hash')
            is_valid = current_hash == original_hash

            return {
                'verified': is_valid,
                'original_hash': original_hash,
                'current_hash': current_hash,
                'signature_data': signature_data,
                'modification_detected': not is_valid
            }

        except Exception as e:
            logger.error(f"Erreur vérification signature: {str(e)}")
            return {
                'verified': False,
                'error': str(e)
            }
