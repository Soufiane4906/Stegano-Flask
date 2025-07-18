from flask import Flask
from flask_cors import CORS
import os

def create_simple_app():
    """Factory pour créer une version simplifiée de l'application Flask."""
    app = Flask(__name__)

    # Configuration de base
    app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')

    # Créer le dossier uploads s'il n'existe pas
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Configuration CORS simple
    CORS(app, resources={
        r"/api/*": {
            "origins": ["*"],  # Autorise toutes les origines en développement
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # Importer et enregistrer les blueprints
    try:
        from app.api.image_routes_v2 import image_bp_v2, init_image_api

        # Enregistrer le blueprint
        app.register_blueprint(image_bp_v2)

        # Initialiser les services
        init_image_api(app)

        print("✅ Blueprint image_routes_v2 enregistré avec succès")
    except ImportError as e:
        print(f"⚠️ Erreur d'import des routes: {e}")
        # Créer une route de test simple
        @app.route('/api/test')
        def test_route():
            return {"status": "ok", "message": "Application simple fonctionne"}

    # Route de base
    @app.route('/')
    def index():
        return {
            "message": "Stegano-Flask API Simple",
            "version": "1.0",
            "endpoints": [
                "/api/v2/upload",
                "/api/v2/add_steganography",
                "/api/v2/verify_integrity",
                "/api/v2/images",
                "/api/test"
            ]
        }

    @app.route('/health')
    def health():
        return {"status": "healthy", "mode": "simple"}

    return app

if __name__ == '__main__':
    app = create_simple_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
