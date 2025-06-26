import pytest
from app.utils.validators import ImageValidator, validate_steganography_message
from app.utils.exceptions import ValidationError
from werkzeug.datastructures import FileStorage
import io

class TestImageValidator:
    """Tests pour le validateur d'images."""

    def test_validate_valid_image(self, sample_image):
        """Test de validation d'une image valide."""
        validator = ImageValidator()

        # Créer un FileStorage mock
        file_storage = FileStorage(
            stream=sample_image,
            filename="test.png",
            content_type="image/png"
        )

        result = validator.validate_image_file(file_storage)

        assert result['is_valid'] is True
        assert result['filename'] == "test.png"
        assert result['width'] == 100
        assert result['height'] == 100

    def test_validate_invalid_extension(self):
        """Test de validation avec extension non autorisée."""
        validator = ImageValidator()

        file_storage = FileStorage(
            stream=io.BytesIO(b"fake content"),
            filename="test.txt",
            content_type="text/plain"
        )

        with pytest.raises(ValidationError) as exc_info:
            validator.validate_image_file(file_storage)

        assert "Extension non autorisée" in str(exc_info.value)

    def test_validate_empty_file(self):
        """Test de validation avec fichier vide."""
        validator = ImageValidator()

        file_storage = FileStorage(
            stream=io.BytesIO(b""),
            filename="test.png",
            content_type="image/png"
        )

        with pytest.raises(ValidationError) as exc_info:
            validator.validate_image_file(file_storage)

        assert "fichier est vide" in str(exc_info.value)

class TestSteganographyValidator:
    """Tests pour le validateur de messages de stéganographie."""

    def test_validate_valid_message(self):
        """Test de validation d'un message valide."""
        message = "Ceci est un message secret"
        result = validate_steganography_message(message)

        assert result['is_valid'] is True
        assert result['message'] == message
        assert result['length'] == len(message)

    def test_validate_empty_message(self):
        """Test de validation avec message vide."""
        with pytest.raises(ValidationError) as exc_info:
            validate_steganography_message("")

        assert "Message vide" in str(exc_info.value)

    def test_validate_too_long_message(self):
        """Test de validation avec message trop long."""
        long_message = "A" * 1001  # Plus de 1000 caractères

        with pytest.raises(ValidationError) as exc_info:
            validate_steganography_message(long_message)

        assert "Message trop long" in str(exc_info.value)
