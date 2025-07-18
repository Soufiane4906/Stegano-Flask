import os
import logging
from flask import Flask, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from config.settings import config
from app.models.image_models import db

def create_app(config_name='default'):
    """
    Factory pour créer l'application Flask.

    Args:
        config_name: Nom de la configuration à utiliser

    Returns:
        Instance de l'application Flask configurée
    """
    # Configurer le chemin des templates (dans le dossier app/templates)
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
    app = Flask(__name__, template_folder=template_dir)

    # Charger la configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Initialiser les extensions
    init_extensions(app)

    # Enregistrer les blueprints
    register_blueprints(app)

    # Configurer les logs
    configure_logging(app)

    # Créer les dossiers nécessaires
    os.makedirs('instance', exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs('logs', exist_ok=True)

    # Créer les tables de base de données
    try:
        with app.app_context():
            db.create_all()
            print("✅ Base de données initialisée avec succès")
    except Exception as e:
        print(f"⚠️ Erreur lors de l'initialisation de la base de données: {e}")
        print("💡 L'application peut continuer sans base de données pour les tests")

    return app

def init_extensions(app):
    """Initialise les extensions Flask."""
    # CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # SQLAlchemy
    db.init_app(app)

def register_blueprints(app):
    """Enregistre les blueprints de l'application."""
    from app.api.image_routes import image_bp, init_image_api
    from app.api.image_routes_v2 import image_bp_v2, init_image_api as init_image_api_v2
    from app.api.jpeg_routes import jpeg_bp
    from app.api.test_interface_routes import test_interface_bp

    # Initialiser l'API d'images (version 1)
    init_image_api(app)

    # Initialiser l'API d'images (version 2)
    init_image_api_v2(app)

    # Enregistrer les blueprints
    app.register_blueprint(image_bp)
    app.register_blueprint(image_bp_v2)
    app.register_blueprint(jpeg_bp)
    app.register_blueprint(test_interface_bp)

    # Routes pour les pages HTML
    @app.route('/')
    def index():
        try:
            return render_template('index.html')
        except Exception:
            # Fallback en cas de problème avec les templates
            return {
                "message": "Stegano-Flask API",
                "version": "2.0.0",
                "status": "running",
                "note": "Templates loading... Please try: /api/status for API info"
            }

    @app.route('/test-templates')
    def test_templates():
        return render_template('test.html')

    @app.route('/simple-test')
    def simple_test():
        return "<h1>Simple Test - Flask fonctionne!</h1><p>Templates dans: app/templates/</p>"

    @app.route('/steganography.html')
    def steganography():
        return render_template('steganography.html')

    @app.route('/ai-detection.html')
    def ai_detection():
        return render_template('ai-detection.html')

    @app.route('/similarity.html')
    def similarity():
        return render_template('similarity.html')

    @app.route('/test-api.html')
    def test_api():
        return render_template('test-api.html')

    # Route API pour les informations
    @app.route('/api/status')
    def api_status():
        return {
            "message": "API Stéganographie Flask",
            "version": "2.0.0",
            "status": "running"
        }

    @app.route('/api/test')
    def api_test():
        return {"status": "ok", "message": "API de test fonctionne"}

    @app.route('/health')
    def health():
        return {"status": "healthy", "message": "API is running"}

def configure_logging(app):
    """Configure le système de logs."""
    if not app.debug and not app.testing:
        # Configuration pour la production
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s %(name)s: %(message)s'
        )
    else:
        # Configuration pour le développement
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)s %(name)s: %(message)s'
        )