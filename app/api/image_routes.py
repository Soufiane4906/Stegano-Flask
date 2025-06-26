from flask import Blueprint, request, jsonify, send_from_directory, current_app
from werkzeug.exceptions import BadRequest
import logging
from app.services.image_service import ImageService
from app.services.ai_detection_service_v2 import AIDetectionService
from app.utils.validators import ImageValidator, validate_steganography_message
from app.utils.exceptions import ValidationError, ImageProcessingError, AIDetectionError, SteganographyError

logger = logging.getLogger(__name__)

# Créer le blueprint
image_bp = Blueprint('images', __name__, url_prefix='/api/images')

# Initialiser les services (sera fait dans app factory)
image_service = None
image_validator = None

def init_image_api(app):
    """Initialise l'API d'images avec les services."""
    global image_service, image_validator

    # Initialiser le service de détection IA
    ai_service = AIDetectionService()

    # Initialiser le service d'images
    image_service = ImageService(app.config['UPLOAD_FOLDER'], ai_service)

    # Initialiser le validateur
    image_validator = ImageValidator(app.config['MAX_CONTENT_LENGTH'])

@image_bp.route('/upload', methods=['POST'])
def upload_and_analyze():
    """
    Endpoint pour télécharger et analyser une image.

    Effectue une analyse complète incluant:
    - Détection de stéganographie
    - Détection d'images générées par IA
    - Extraction de métadonnées
    - Recherche d'images similaires
    """
    try:
        # Vérifier qu'un fichier est fourni
        if 'file' not in request.files:
            return jsonify({"error": "Aucun fichier fourni"}), 400

        file = request.files['file']

        # Valider le fichier
        image_validator.validate_image_file(file)

        # Traiter l'image
        result = image_service.process_uploaded_image(file)

        return jsonify({
            "success": True,
            "data": result
        }), 200

    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except (ImageProcessingError, AIDetectionError, SteganographyError) as e:
        logger.error(f"Erreur lors du traitement: {str(e)}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.error(f"Erreur inattendue: {str(e)}")
        return jsonify({"error": "Erreur interne du serveur"}), 500

@image_bp.route('/steganography/add', methods=['POST'])
def add_steganography():
    """
    Endpoint pour ajouter un message caché à une image.
    """
    try:
        # Vérifier qu'un fichier et un message sont fournis
        if 'file' not in request.files:
            return jsonify({"error": "Aucun fichier fourni"}), 400

        if 'message' not in request.form:
            return jsonify({"error": "Aucun message fourni"}), 400

        file = request.files['file']
        message = request.form['message']

        # Valider le fichier
        image_validator.validate_image_file(file)

        # Valider le message
        validate_steganography_message(message)

        # Ajouter la stéganographie
        result = image_service.add_steganography_to_image(file, message)

        return jsonify({
            "success": True,
            "data": result
        }), 200

    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except (ImageProcessingError, SteganographyError) as e:
        logger.error(f"Erreur lors de l'ajout de stéganographie: {str(e)}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.error(f"Erreur inattendue: {str(e)}")
        return jsonify({"error": "Erreur interne du serveur"}), 500

@image_bp.route('/steganography/detect', methods=['POST'])
def detect_steganography():
    """
    Endpoint pour détecter uniquement la stéganographie dans une image.
    """
    try:
        if 'file' not in request.files:
            return jsonify({"error": "Aucun fichier fourni"}), 400

        file = request.files['file']

        # Valider le fichier
        image_validator.validate_image_file(file)

        # Sauvegarder temporairement le fichier
        filename, filepath = image_service._save_uploaded_file(file)

        # Détecter la stéganographie
        from app.services.steganography_service import SteganographyService
        steg_service = SteganographyService()
        result = steg_service.detect_hidden_message(filepath)

        # Format pour l'interface web (compatibilité avec steganography.html)
        if result.get('signature_detected'):
            return jsonify({
                "success": True,
                "message": result.get('signature', ''),
                "data": {
                    "filename": filename,
                    "steganography": result
                }
            }), 200
        else:
            return jsonify({
                "success": True,
                "message": None,
                "data": {
                    "filename": filename,
                    "steganography": result
                }
            }), 200

    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except SteganographyError as e:
        logger.error(f"Erreur lors de la détection: {str(e)}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.error(f"Erreur inattendue: {str(e)}")
        return jsonify({"error": "Erreur interne du serveur"}), 500

@image_bp.route('/ai-detection', methods=['POST'])
def detect_ai_generated():
    """
    Endpoint pour détecter uniquement si une image est générée par IA.
    """
    try:
        if 'file' not in request.files:
            return jsonify({"error": "Aucun fichier fourni"}), 400

        file = request.files['file']

        # Valider le fichier
        image_validator.validate_image_file(file)

        # Sauvegarder temporairement le fichier
        filename, filepath = image_service._save_uploaded_file(file)

        # Détecter si l'image est générée par IA
        result = image_service.ai_service.detect_ai_image(filepath)

        return jsonify({
            "success": True,
            "data": {
                "filename": filename,
                "ai_detection": result
            }
        }), 200

    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except AIDetectionError as e:
        logger.error(f"Erreur lors de la détection IA: {str(e)}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.error(f"Erreur inattendue: {str(e)}")
        return jsonify({"error": "Erreur interne du serveur"}), 500

@image_bp.route('/history')
def get_analysis_history():
    """
    Endpoint pour récupérer l'historique des analyses.
    """
    try:
        limit = request.args.get('limit', 50, type=int)
        user_id = request.args.get('user_id', type=int)

        # Limiter le nombre de résultats
        if limit > 100:
            limit = 100

        history = image_service.get_analysis_history(user_id=user_id, limit=limit)

        return jsonify({
            "success": True,
            "data": {
                "analyses": history,
                "count": len(history)
            }
        }), 200

    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'historique: {str(e)}")
        return jsonify({"error": "Impossible de récupérer l'historique"}), 500

@image_bp.route('/uploads/<filename>')
def get_uploaded_file(filename):
    """
    Endpoint pour servir les fichiers téléchargés.
    """
    try:
        return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
    except FileNotFoundError:
        return jsonify({"error": "Fichier introuvable"}), 404
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du fichier: {str(e)}")
        return jsonify({"error": "Erreur lors de la récupération du fichier"}), 500

@image_bp.route('/health')
def health_check():
    """
    Endpoint de vérification de l'état de santé de l'API.
    """
    try:
        # Vérifier l'état des services
        ai_status = "OK" if image_service.ai_service.is_model_loaded() else "Modèle non chargé"

        return jsonify({
            "success": True,
            "data": {
                "status": "healthy",
                "services": {
                    "image_service": "OK",
                    "ai_detection": ai_status,
                    "steganography": "OK"
                }
            }
        }), 200

    except Exception as e:
        logger.error(f"Erreur lors de la vérification de santé: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Erreur lors de la vérification"
        }), 500

# Gestionnaire d'erreurs pour le blueprint
@image_bp.errorhandler(BadRequest)
def handle_bad_request(e):
    """Gestionnaire pour les erreurs de requête malformée."""
    return jsonify({"error": "Requête malformée"}), 400

@image_bp.errorhandler(413)
def handle_file_too_large(e):
    """Gestionnaire pour les fichiers trop volumineux."""
    return jsonify({"error": "Fichier trop volumineux"}), 413

@image_bp.errorhandler(Exception)
def handle_unexpected_error(e):
    """Gestionnaire pour les erreurs inattendues."""
    logger.error(f"Erreur inattendue dans l'API: {str(e)}")
    return jsonify({"error": "Erreur interne du serveur"}), 500

@image_bp.route('/hide', methods=['POST'])
def hide_message():
    """Alias pour steganography/add - Cacher un message dans une image."""
    return add_steganography()

@image_bp.route('/reveal', methods=['POST'])
def reveal_message():
    """Alias pour steganography/detect - Révéler un message caché."""
    return detect_steganography()

@image_bp.route('/similarity', methods=['POST'])
def compare_similarity():
    """
    Endpoint pour comparer la similarité entre deux images.
    """
    try:
        # Vérifier que deux fichiers sont fournis
        if 'file1' not in request.files or 'file2' not in request.files:
            return jsonify({"error": "Deux fichiers sont requis (file1 et file2)"}), 400

        file1 = request.files['file1']
        file2 = request.files['file2']

        # Valider les fichiers
        image_validator.validate_image_file(file1)
        image_validator.validate_image_file(file2)

        # Traiter les images avec le service
        service_result = image_service.compare_similarity(file1, file2)

        # Vérifier que le service a retourné des données valides
        if not service_result or 'similarity' not in service_result:
            return jsonify({"error": "Erreur dans le calcul de similarité"}), 500

        similarity_data = service_result.get('similarity', {})

        # Sécuriser l'accès aux données de similarité
        phash_score = similarity_data.get('phash', 0)
        dhash_score = similarity_data.get('dhash', 0)
        average_score = similarity_data.get('average', 0)

        # Adapter le format pour l'interface web (les scores sont déjà en pourcentage 0-100)
        web_result = {
            "status": "success",
            "similarity_score": average_score,  # Garder en pourcentage
            "details": {
                "phash": phash_score,
                "dhash": dhash_score,
                "average": average_score,
                "structural": average_score  # Alias pour l'interface
            },
            "files": service_result.get("files", {}),
            "method": service_result.get("method", "steganoV2_hamming_distance"),
            "identical": service_result.get("identical", False),
            "similar": service_result.get("similar", False),
            "timestamp": service_result.get("timestamp", ""),
            # Données complètes pour l'API
            "raw_data": service_result
        }

        logger.info("Comparaison de similarité effectuée avec succès")
        return jsonify(web_result)

    except ValidationError as e:
        logger.error(f"Erreur de validation: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Erreur lors de la comparaison de similarité: {str(e)}")
        logger.error(f"Type d'erreur: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback complet: {traceback.format_exc()}")
        return jsonify({"error": f"Erreur interne du serveur: {str(e)}"}), 500
