import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration de base pour l'application."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB max

    # Base de données
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///instance/app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Modèles AI
    AI_MODEL_PATH = os.environ.get('AI_MODEL_PATH') or 'modelFakeReal.h5'

    # Stéganographie
    SIMILARITY_THRESHOLD = float(os.environ.get('SIMILARITY_THRESHOLD', 0.85))

    # Sécurité
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}

    @staticmethod
    def init_app(app):
        """Initialise l'application avec la configuration."""
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

class DevelopmentConfig(Config):
    """Configuration pour le développement."""
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    """Configuration pour la production."""
    DEBUG = False
    FLASK_ENV = 'production'

class TestingConfig(Config):
    """Configuration pour les tests."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    UPLOAD_FOLDER = 'test_uploads'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
