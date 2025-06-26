#!/usr/bin/env python3
"""
Version simplifiée de l'application pour les tests sans base de données.
"""

import os
from flask import Flask, jsonify, request
from flask_cors import CORS

def create_simple_app():
    """Crée une version simplifiée de l'application."""
    app = Flask(__name__)

    # Configuration de base
    app.config['SECRET_KEY'] = 'dev-secret-key'
    app.config['UPLOAD_FOLDER'] = 'uploads'

    # CORS
    CORS(app)

    # Créer les dossiers
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('logs', exist_ok=True)

    @app.route('/')
    def index():
        return {
            "message": "API Stéganographie Flask - Version Simple",
            "version": "2.0.0-simple",
            "status": "running"
        }

    @app.route('/health')
    def health():
        return {"status": "healthy", "message": "API simple fonctionne"}

    @app.route('/api/test')
    def test_api():
        return {
            "success": True,
            "message": "API fonctionnelle",
            "features_available": {
                "upload": "Simulation disponible",
                "steganography": "Disponible avec le package stegano",
                "database": "Désactivée dans cette version"
            }
        }

    @app.route('/api/upload', methods=['POST'])
    def upload_image():
        """Endpoint simulé pour l'upload d'images."""
        try:
            # Vérifier si un fichier est présent
            if 'image' not in request.files:
                return jsonify({
                    "success": False,
                    "error": "Aucun fichier image fourni"
                }), 400

            file = request.files['image']

            if file.filename == '':
                return jsonify({
                    "success": False,
                    "error": "Aucun fichier sélectionné"
                }), 400

            # Simuler la sauvegarde
            filename = file.filename
            file_size = len(file.read())
            file.seek(0)  # Reset file pointer

            return jsonify({
                "success": True,
                "message": "Image uploadée avec succès (simulation)",
                "data": {
                    "filename": filename,
                    "size": file_size,
                    "note": "Version simple - Fonctionnalités de stéganographie non implémentées",
                    "available_operations": [
                        "hide_message (nécessite app complète)",
                        "extract_message (nécessite app complète)",
                        "detect_ai (nécessite TensorFlow)"
                    ]
                }
            })

        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"Erreur lors de l'upload: {str(e)}"
            }), 500

    @app.route('/api/extract', methods=['POST'])
    def extract_message():
        """Endpoint simulé pour l'extraction de messages."""
        return jsonify({
            "success": False,
            "error": "Fonctionnalité non disponible dans la version simple",
            "message": "Utilisez 'python run.py' pour la version complète"
        }), 501

    @app.route('/api/detect', methods=['POST'])
    def detect_ai():
        """Endpoint simulé pour la détection IA."""
        return jsonify({
            "success": False,
            "error": "Détection IA non disponible - TensorFlow requis",
            "message": "Cette fonctionnalité nécessite TensorFlow et le modèle de détection"
        }), 501

    return app

if __name__ == '__main__':
    print("🚀 Démarrage de l'application simple...")
    app = create_simple_app()
    print("📍 Application disponible sur http://localhost:5000")
    print("🔗 Test: http://localhost:5000/api/test")
    print("📤 Upload (simulé): http://localhost:5000/api/upload")

    app.run(debug=True, host='127.0.0.1', port=5000)
