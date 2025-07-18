from flask import Blueprint, render_template, request, jsonify, current_app
import os

# Créer le blueprint pour l'interface de test
test_interface_bp = Blueprint('test_interface', __name__)

@test_interface_bp.route('/test')
def jpeg_test_interface():
    """Interface de test HTML pour l'API JPEG Steganography"""
    return render_template('jpeg_test.html')

@test_interface_bp.route('/test/status')
def test_status():
    """Endpoint pour vérifier le statut de l'application"""
    return jsonify({
        'status': 'ok',
        'message': 'Interface de test JPEG Steganography opérationnelle',
        'api_base': '/api/v2/jpeg',
        'upload_folder': current_app.config.get('UPLOAD_FOLDER', 'uploads'),
        'test_images_available': os.path.exists('test_images')
    })

@test_interface_bp.route('/test/files')
def list_test_files():
    """Liste les fichiers de test disponibles"""
    test_files = []
    upload_files = []

    # Fichiers de test
    if os.path.exists('test_images'):
        for file in os.listdir('test_images'):
            if file.lower().endswith(('.jpg', '.jpeg')):
                file_path = os.path.join('test_images', file)
                file_size = os.path.getsize(file_path)
                test_files.append({
                    'name': file,
                    'path': f'test_images/{file}',
                    'size': file_size,
                    'size_kb': round(file_size / 1024, 2)
                })

    # Fichiers uploadés
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    if os.path.exists(upload_folder):
        for file in os.listdir(upload_folder):
            if file.lower().endswith(('.jpg', '.jpeg')):
                file_path = os.path.join(upload_folder, file)
                file_size = os.path.getsize(file_path)
                upload_files.append({
                    'name': file,
                    'path': f'{upload_folder}/{file}',
                    'size': file_size,
                    'size_kb': round(file_size / 1024, 2)
                })

    return jsonify({
        'test_images': test_files,
        'uploaded_files': upload_files,
        'total_test_images': len(test_files),
        'total_uploaded_files': len(upload_files)
    })

@test_interface_bp.route('/test/help')
def test_help():
    """Guide d'utilisation de l'interface de test"""
    help_info = {
        'title': 'Guide d\'utilisation - Interface de Test JPEG Steganography',
        'sections': [
            {
                'title': 'Préparation',
                'steps': [
                    'Assurez-vous que votre application Flask est démarrée',
                    'Placez des images JPEG de test dans le dossier test_images/',
                    'Vérifiez que le dossier uploads/ existe pour les fichiers générés'
                ]
            },
            {
                'title': 'Tests disponibles',
                'tests': [
                    {
                        'name': 'Méthodes disponibles',
                        'description': 'Affiche les méthodes de stéganographie supportées'
                    },
                    {
                        'name': 'Analyse de capacité',
                        'description': 'Calcule combien de caractères peuvent être cachés'
                    },
                    {
                        'name': 'Dissimulation de message',
                        'description': 'Cache un message dans une image avec EXIF ou LSB'
                    },
                    {
                        'name': 'Extraction de message',
                        'description': 'Récupère un message caché dans une image'
                    },
                    {
                        'name': 'Signature stéganographique',
                        'description': 'Crée et vérifie des signatures invisibles'
                    },
                    {
                        'name': 'Test complet automatique',
                        'description': 'Exécute tous les tests avec une seule image'
                    }
                ]
            },
            {
                'title': 'Conseils d\'utilisation',
                'tips': [
                    'Commencez par analyser la capacité avant de dissimuler',
                    'La méthode EXIF est limitée mais plus simple',
                    'La méthode LSB peut cacher plus de données',
                    'Testez l\'extraction immédiatement après la dissimulation',
                    'Les signatures permettent de vérifier l\'intégrité'
                ]
            }
        ],
        'endpoints': {
            'interface': '/test',
            'status': '/test/status',
            'files': '/test/files',
            'help': '/test/help'
        }
    }

    return jsonify(help_info)
