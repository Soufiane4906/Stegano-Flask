import os
from typing import Dict, Any, List
from werkzeug.datastructures import FileStorage
from app.utils.exceptions import ValidationError, FileUploadError

class FileValidator:
    """Validateur pour les fichiers téléchargés."""

    def __init__(self, allowed_extensions: set, max_size: int = 16 * 1024 * 1024):
        """
        Initialise le validateur.

        Args:
            allowed_extensions: Extensions autorisées
            max_size: Taille maximale en bytes
        """
        self.allowed_extensions = allowed_extensions
        self.max_size = max_size

    def validate_file(self, file: FileStorage) -> Dict[str, Any]:
        """
        Valide un fichier téléchargé.

        Args:
            file: Fichier à valider

        Returns:
            Dictionnaire avec les informations de validation

        Raises:
            ValidationError: Si le fichier n'est pas valide
        """
        errors = []

        # Vérifier si un fichier est fourni
        if not file or not file.filename:
            raise ValidationError("Aucun fichier fourni")

        # Vérifier l'extension
        if not self._is_allowed_extension(file.filename):
            errors.append(f"Extension non autorisée. Extensions autorisées: {', '.join(self.allowed_extensions)}")

        # Vérifier la taille (si possible)
        if hasattr(file, 'content_length') and file.content_length:
            if file.content_length > self.max_size:
                errors.append(f"Fichier trop volumineux. Taille maximale: {self.max_size / (1024*1024):.1f} MB")

        # Vérifier que le fichier n'est pas vide
        file.seek(0, 2)  # Aller à la fin
        size = file.tell()
        file.seek(0)  # Revenir au début

        if size == 0:
            errors.append("Le fichier est vide")
        elif size > self.max_size:
            errors.append(f"Fichier trop volumineux. Taille maximale: {self.max_size / (1024*1024):.1f} MB")

        if errors:
            raise ValidationError("; ".join(errors))

        return {
            "filename": file.filename,
            "size": size,
            "is_valid": True
        }

    def _is_allowed_extension(self, filename: str) -> bool:
        """Vérifie si l'extension est autorisée."""
        if not filename:
            return False

        extension = filename.rsplit('.', 1)[-1].lower()
        return extension in self.allowed_extensions

class ImageValidator(FileValidator):
    """Validateur spécialisé pour les images."""

    def __init__(self, max_size: int = 16 * 1024 * 1024):
        """Initialise le validateur d'images."""
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}
        super().__init__(allowed_extensions, max_size)

    def validate_image_file(self, file: FileStorage) -> Dict[str, Any]:
        """
        Valide un fichier image avec des vérifications supplémentaires.

        Args:
            file: Fichier image à valider

        Returns:
            Dictionnaire avec les informations de validation
        """
        # Validation de base
        result = self.validate_file(file)

        # Vérifications supplémentaires pour les images
        try:
            from PIL import Image

            # Vérifier que c'est vraiment une image
            file.seek(0)
            with Image.open(file) as img:
                result.update({
                    "width": img.width,
                    "height": img.height,
                    "format": img.format,
                    "mode": img.mode
                })

                # Vérifier les dimensions minimales
                if img.width < 10 or img.height < 10:
                    raise ValidationError("Image trop petite (minimum 10x10 pixels)")

                # Vérifier les dimensions maximales
                if img.width > 10000 or img.height > 10000:
                    raise ValidationError("Image trop grande (maximum 10000x10000 pixels)")

            file.seek(0)  # Remettre au début pour la suite

        except Exception as e:
            raise ValidationError(f"Fichier image invalide: {str(e)}")

        return result

def validate_steganography_message(message: str) -> Dict[str, Any]:
    """
    Valide un message pour la stéganographie.

    Args:
        message: Message à valider

    Returns:
        Dictionnaire avec les informations de validation
    """
    if not message:
        raise ValidationError("Message vide")

    if len(message) > 1000:
        raise ValidationError("Message trop long (maximum 1000 caractères)")

    # Vérifier les caractères autorisés (éviter les caractères de contrôle)
    if any(ord(c) < 32 and c not in '\n\r\t' for c in message):
        raise ValidationError("Message contient des caractères non autorisés")

    return {
        "message": message,
        "length": len(message),
        "is_valid": True
    }

def validate_analysis_request(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Valide une requête d'analyse.

    Args:
        data: Données de la requête

    Returns:
        Données validées
    """
    required_fields = ['file']
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        raise ValidationError(f"Champs manquants: {', '.join(missing_fields)}")

    return data
