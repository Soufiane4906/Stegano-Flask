"""
Routes API spécialisées pour la stéganographie JPEG.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_cors import cross_origin
import os
import logging
from werkzeug.utils import secure_filename
from app.services.jpeg_steganography_service import JPEGSteganographyService
from app.utils.validators import ImageValidator
from app.utils.exceptions import ValidationError

logger = logging.getLogger(__name__)

# Créer le blueprint pour les routes JPEG
jpeg_bp = Blueprint('jpeg_stegano', __name__, url_prefix='/api/v2/jpeg')

# Initialiser le service
jpeg_service = JPEGSteganographyService()

@jpeg_bp.route('/analyze_capacity', methods=['POST'])
@cross_origin()
def analyze_jpeg_capacity():
    """Analyse la capacité de dissimulation d'une image JPEG."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier fourni'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nom de fichier vide'}), 400

        # Sauvegarder temporairement le fichier
        filename = secure_filename(file.filename)
        temp_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f"temp_{filename}")
        file.save(temp_path)

        try:
            # Analyser la capacité
            capacity_info = jpeg_service.analyze_jpeg_capacity(temp_path)

            if 'error' in capacity_info:
                return jsonify({
                    'success': False,
                    'error': capacity_info['error']
                }), 400

            return jsonify({
                'success': True,
                'filename': filename,
                'capacity_analysis': capacity_info
            })

        finally:
            # Nettoyer le fichier temporaire
            if os.path.exists(temp_path):
                os.remove(temp_path)

    except Exception as e:
        logger.error(f"Erreur analyse capacité JPEG: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Erreur lors de l\'analyse: {str(e)}'
        }), 500

@jpeg_bp.route('/hide_message', methods=['POST'])
@cross_origin()
def hide_message_in_jpeg():
    """Cache un message dans une image JPEG."""
    try:
        # Vérifier les données requises
        if 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier fourni'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nom de fichier vide'}), 400

        message = request.form.get('message', '').strip()
        if not message:
            return jsonify({'error': 'Message requis'}), 400

        method = request.form.get('method', 'exif').lower()
        if method not in ['exif', 'lsb', 'dct']:
            return jsonify({'error': 'Méthode non supportée'}), 400

        # Sauvegarder le fichier d'entrée
        filename = secure_filename(file.filename)
        input_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(input_path)

        # Générer le nom du fichier de sortie
        base_name, ext = os.path.splitext(filename)
        output_filename = f"{base_name}_stego_{method}{ext}"
        output_path = os.path.join(current_app.config['UPLOAD_FOLDER'], output_filename)

        # Cacher le message
        result = jpeg_service.hide_message_in_jpeg(
            input_path,
            message,
            output_path,
            method=method
        )

        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Message caché avec succès',
                'input_filename': filename,
                'output_filename': output_filename,
                'method': method,
                'message_length': result['message_length'],
                'details': {
                    key: value for key, value in result.items()
                    if key not in ['success', 'input_path', 'output_path']
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Erreur inconnue')
            }), 400

    except Exception as e:
        logger.error(f"Erreur dissimulation JPEG: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Erreur lors de la dissimulation: {str(e)}'
        }), 500

@jpeg_bp.route('/extract_message', methods=['POST'])
@cross_origin()
def extract_message_from_jpeg():
    """Extrait un message caché d'une image JPEG."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier fourni'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nom de fichier vide'}), 400

        method = request.form.get('method', 'exif').lower()
        if method not in ['exif', 'lsb', 'dct']:
            return jsonify({'error': 'Méthode non supportée'}), 400

        # Sauvegarder temporairement le fichier
        filename = secure_filename(file.filename)
        temp_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f"extract_{filename}")
        file.save(temp_path)

        try:
            # Extraire le message
            result = jpeg_service.extract_message_from_jpeg(temp_path, method=method)

            if result['success']:
                response_data = {
                    'success': True,
                    'filename': filename,
                    'method': method,
                    'message_found': result.get('message') is not None
                }

                if result.get('message'):
                    response_data['message'] = result['message']
                    response_data['message_length'] = len(result['message'])
                else:
                    response_data['info'] = result.get('info', 'Aucun message trouvé')

                return jsonify(response_data)
            else:
                return jsonify({
                    'success': False,
                    'error': result.get('error', 'Erreur inconnue')
                }), 400

        finally:
            # Nettoyer le fichier temporaire
            if os.path.exists(temp_path):
                os.remove(temp_path)

    except Exception as e:
        logger.error(f"Erreur extraction JPEG: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Erreur lors de l\'extraction: {str(e)}'
        }), 500

@jpeg_bp.route('/create_signature', methods=['POST'])
@cross_origin()
def create_steganographic_signature():
    """Crée une signature stéganographique pour une image JPEG."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier fourni'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nom de fichier vide'}), 400

        # Sauvegarder le fichier d'entrée
        filename = secure_filename(file.filename)
        input_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(input_path)

        # Générer le nom du fichier signé
        base_name, ext = os.path.splitext(filename)
        signed_filename = f"{base_name}_signed{ext}"
        signed_path = os.path.join(current_app.config['UPLOAD_FOLDER'], signed_filename)

        # Créer la signature
        result = jpeg_service.create_steganographic_signature(input_path, signed_path)

        if result.get('success'):
            return jsonify({
                'success': True,
                'message': 'Signature créée avec succès',
                'input_filename': filename,
                'signed_filename': signed_filename,
                'signature_info': {
                    'content_hash': result['signature_data']['content_hash'][:16] + '...',
                    'timestamp': result['signature_data']['timestamp'],
                    'dimensions': result['signature_data']['dimensions']
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Erreur inconnue')
            }), 400

    except Exception as e:
        logger.error(f"Erreur création signature: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Erreur lors de la création de signature: {str(e)}'
        }), 500

@jpeg_bp.route('/verify_signature', methods=['POST'])
@cross_origin()
def verify_steganographic_signature():
    """Vérifie l'intégrité d'une signature stéganographique."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier fourni'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nom de fichier vide'}), 400

        # Sauvegarder temporairement le fichier
        filename = secure_filename(file.filename)
        temp_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f"verify_{filename}")
        file.save(temp_path)

        try:
            # Vérifier la signature
            result = jpeg_service.verify_steganographic_signature(temp_path)

            return jsonify({
                'success': True,
                'filename': filename,
                'verification_result': {
                    'verified': result['verified'],
                    'reason': result.get('reason'),
                    'modification_detected': result.get('modification_detected', False),
                    'signature_found': 'signature_data' in result
                },
                'details': result if result['verified'] else None
            })

        finally:
            # Nettoyer le fichier temporaire
            if os.path.exists(temp_path):
                os.remove(temp_path)

    except Exception as e:
        logger.error(f"Erreur vérification signature: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Erreur lors de la vérification: {str(e)}'
        }), 500

@jpeg_bp.route('/methods', methods=['GET'])
@cross_origin()
def get_available_methods():
    """Retourne les méthodes de stéganographie disponibles pour JPEG."""
    return jsonify({
        'success': True,
        'methods': {
            'exif': {
                'name': 'EXIF Steganography',
                'description': 'Cache le message dans les métadonnées EXIF',
                'capacity': 'Jusqu\'à 32KB',
                'detection_difficulty': 'Faible',
                'image_quality_impact': 'Aucun'
            },
            'lsb': {
                'name': 'LSB Steganography',
                'description': 'Modifie les bits de poids faible des pixels',
                'capacity': 'Variable selon la taille d\'image',
                'detection_difficulty': 'Moyenne',
                'image_quality_impact': 'Très faible'
            },
            'dct': {
                'name': 'DCT Coefficient Modification',
                'description': 'Modifie les coefficients DCT (en développement)',
                'capacity': 'Variable',
                'detection_difficulty': 'Élevée',
                'image_quality_impact': 'Faible'
            }
        },
        'recommended_usage': {
            'small_messages': 'exif',
            'large_messages': 'lsb',
            'high_security': 'dct'
        }
    })

# Export du blueprint
__all__ = ['jpeg_bp']
