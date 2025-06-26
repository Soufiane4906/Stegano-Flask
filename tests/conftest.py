import pytest
import os
import tempfile
from app import create_app
from app.models.image_models import db

@pytest.fixture
def app():
    """Fixture pour créer une application de test."""
    app = create_app('testing')

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Fixture pour créer un client de test."""
    return app.test_client()

@pytest.fixture
def sample_image():
    """Fixture pour créer une image de test."""
    from PIL import Image
    import io

    # Créer une image simple
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    return img_bytes
