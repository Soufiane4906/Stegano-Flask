from flask import Blueprint, request, jsonify, send_from_directory, current_app
from werkzeug.exceptions import BadRequest
import logging
import os
import uuid
from datetime import datetime
from app.services.image_service import ImageService
from app.services.ai_detection_service_v2 import AIDetectionService
from app.services.steganography_service import SteganographyService
from app.services.advanced_steganography_service import AdvancedSteganographyService
from app.models.image_models import ImageAnalysis, db
from app.utils.validators import ImageValidator, validate_steganography_message
from app.utils.exceptions import ValidationError, ImageProcessingError, AIDetectionError, SteganographyError

logger = logging.getLogger(__name__)

# Créer le blueprint v2 avec un nom unique
image_bp_v2 = Blueprint('images_v2', __name__, url_prefix='/api/v2')

# Initialiser les services globaux
image_service = None
ai_service = None
stego_service = None
advanced_stego_service = None
image_validator = None

def init_image_api(app):
    """Initialise l'API d'images avec les services."""
    global image_service, ai_service, stego_service, advanced_stego_service, image_validator

    # Initialiser les services
    ai_service = AIDetectionService()
    stego_service = SteganographyService()
    advanced_stego_service = AdvancedSteganographyService()
    image_service = ImageService(app.config['UPLOAD_FOLDER'], ai_service)
    image_validator = ImageValidator(app.config['MAX_CONTENT_LENGTH'])

    logger.info("✅ Services d'images avancés initialisés")

@image_bp_v2.route('/upload', methods=['POST'])
def upload_and_analyze():
    """
    Endpoint pour télécharger et analyser une image.
    Analyse complète avec stéganographie, IA et similarité.
    """
    try:
        # Vérifier qu'un fichier est fourni
        if 'file' not in request.files:
            return jsonify({"error": "Aucun fichier fourni"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "Aucun fichier sélectionné"}), 400

        # Valider le fichier
        try:
            image_validator.validate_image_file(file)
        except ValidationError as e:
            return jsonify({"error": str(e)}), 400

        # Paramètres optionnels
        skip_analysis = request.args.get('skip_analysis') == 'true'
        only_check_similar = request.args.get('only_check_similar') == 'true'

        # Créer un nom de fichier unique
        filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

        # Sauvegarder le fichier
        file.save(filepath)

        # Générer les hashes pour la détection de similarité
        hashes = stego_service.generate_image_hashes(filepath)

        # Rechercher des images similaires
        similar_images = stego_service.find_similar_images_advanced(hashes)

        # Si on ne veut que vérifier les similaires
        if only_check_similar:
            os.remove(filepath)  # Supprimer le fichier temporaire
            return jsonify({
                "similar_images": similar_images,
                "similar_found": len(similar_images) > 0
            })

        # Analyse complète
        analysis_results = {}

        # 1. Analyse de stéganographie
        try:
            stego_result = stego_service.detect_hidden_message(filepath)
            analysis_results['steganography'] = stego_result
        except Exception as e:
            logger.error(f"Erreur analyse stéganographie: {str(e)}")
            analysis_results['steganography'] = {"error": str(e)}

        # 2. Détection IA
        try:
            ai_result = ai_service.detect_ai_image(filepath)
            analysis_results['ai_detection'] = ai_result
        except Exception as e:
            logger.error(f"Erreur détection IA: {str(e)}")
            analysis_results['ai_detection'] = {"error": str(e)}

        # 3. Métadonnées
        try:
            metadata = get_image_metadata(filepath)
            analysis_results['metadata'] = metadata
        except Exception as e:
            logger.error(f"Erreur métadonnées: {str(e)}")
            analysis_results['metadata'] = {"error": str(e)}

        # 4. Signature contextuelle
        try:
            context_signature = stego_service.generate_image_context_signature(filepath)
            analysis_results['context_signature'] = context_signature
        except Exception as e:
            logger.error(f"Erreur signature contextuelle: {str(e)}")
            analysis_results['context_signature'] = None

        # Sauvegarder en base de données
        try:
            image_analysis = ImageAnalysis(
                filename=os.path.basename(file.filename),
                image_path=filepath,
                perceptual_hash=hashes.get("phash"),
                md5_hash=stego_service.calculate_md5_hash(filepath),
                ai_confidence=analysis_results.get('ai_detection', {}).get('confidence', 0),
                has_steganography=analysis_results.get('steganography', {}).get('signature_detected', False),
                metadata_json=str(analysis_results.get('metadata', {})),
                upload_timestamp=datetime.utcnow()
            )

            db.session.add(image_analysis)
            db.session.commit()

            image_id = image_analysis.id

        except Exception as e:
            logger.error(f"Erreur sauvegarde DB: {str(e)}")
            image_id = None

        # Réponse finale
        return jsonify({
            "image_id": image_id,
            "filename": filename,
            "image_path": filepath,
            "analysis": analysis_results,
            "perceptual_hashes": hashes,
            "similar_images": similar_images,
            "similar_found": len(similar_images) > 0,
            "upload_timestamp": datetime.utcnow().isoformat()
        })

    except Exception as e:
        logger.error(f"Erreur upload et analyse: {str(e)}")
        return jsonify({"error": f"Erreur lors de l'analyse: {str(e)}"}), 500

@image_bp_v2.route('/add_steganography', methods=['POST'])
def add_steganography():
    """
    Endpoint pour ajouter une signature stéganographique à une image.
    """
    try:
        # Vérifier qu'un fichier est fourni
        if 'file' not in request.files:
            return jsonify({"error": "Aucun fichier fourni"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "Aucun fichier sélectionné"}), 400

        # Récupérer la signature utilisateur
        user_signature = request.form.get('signature', '')

        # Valider le fichier
        try:
            image_validator.validate_image_file(file)
        except ValidationError as e:
            return jsonify({"error": str(e)}), 400

        # Créer un nom de fichier unique
        filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

        # Sauvegarder le fichier
        file.save(filepath)

        # Générer la signature contextuelle
        context_signature = stego_service.generate_image_context_signature(filepath)

        # Combiner les signatures si nécessaire
        if user_signature:
            combined_signature = f"{user_signature}||{context_signature}"
        else:
            combined_signature = context_signature

        # Embedder la signature
        output_filepath = stego_service.embed_message(filepath, combined_signature)

        # Générer les hashes pour l'image avec stéganographie
        output_hashes = stego_service.generate_image_hashes(output_filepath)

        # Rechercher des images similaires
        similar_images = stego_service.find_similar_images_advanced(output_hashes)

        # Analyser l'image de sortie
        ai_result = ai_service.detect_ai_image(output_filepath)
        metadata = get_image_metadata(output_filepath)

        # Sauvegarder en base de données
        try:
            image_analysis = ImageAnalysis(
                filename=os.path.basename(file.filename),
                image_path=output_filepath,
                perceptual_hash=output_hashes.get("phash"),
                md5_hash=stego_service.calculate_md5_hash(output_filepath),
                ai_confidence=ai_result.get('confidence', 0),
                has_steganography=True,
                metadata_json=str(metadata),
                upload_timestamp=datetime.utcnow()
            )

            db.session.add(image_analysis)
            db.session.commit()

            image_id = image_analysis.id

        except Exception as e:
            logger.error(f"Erreur sauvegarde DB: {str(e)}")
            image_id = None

        # URL publique pour l'image
        output_filename = os.path.basename(output_filepath)
        public_url = f"/api/uploads/{output_filename}"

        return jsonify({
            "message": "Signature ajoutée avec succès",
            "image_id": image_id,
            "image_url": public_url,
            "filename": output_filename,
            "context_signature": context_signature,
            "user_signature": user_signature,
            "ai_detection": ai_result,
            "metadata": metadata,
            "similar_images": similar_images,
            "similar_found": len(similar_images) > 0
        })

    except Exception as e:
        logger.error(f"Erreur ajout stéganographie: {str(e)}")
        return jsonify({"error": f"Erreur lors de l'ajout de signature: {str(e)}"}), 500

@image_bp_v2.route('/verify_integrity', methods=['POST'])
def verify_integrity():
    """
    Endpoint pour vérifier l'intégrité d'une image avec signature.
    """
    try:
        if 'file' not in request.files:
            return jsonify({"error": "Aucun fichier fourni"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "Aucun fichier sélectionné"}), 400

        # Créer un fichier temporaire
        temp_filename = "temp_" + str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
        temp_filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], temp_filename)
        file.save(temp_filepath)

        try:
            # Analyser la stéganographie
            steg_result = stego_service.detect_hidden_message(temp_filepath)

            # Générer la signature contextuelle actuelle
            current_context_signature = stego_service.generate_image_context_signature(temp_filepath)

            # Analyser les signatures intégrées
            embedded_signature = steg_result.get("signature", "")
            embedded_context_signature = ""
            user_signature = ""

            if embedded_signature and "||" in embedded_signature:
                # Format combiné: "user_sig||context_sig"
                user_signature, embedded_context_signature = embedded_signature.split("||", 1)
            elif embedded_signature and embedded_signature.startswith("CV:"):
                # Seulement signature contextuelle
                embedded_context_signature = embedded_signature

            # Comparer les signatures
            signatures_match = embedded_context_signature == current_context_signature

            # Rechercher des images similaires
            hashes = stego_service.generate_image_hashes(temp_filepath)
            similar_images = stego_service.find_similar_images_advanced(hashes)

            result = {
                "steganography_detected": steg_result.get("signature_detected", False),
                "current_context_signature": current_context_signature,
                "embedded_context_signature": embedded_context_signature,
                "user_signature": user_signature,
                "signatures_match": signatures_match,
                "tampered": bool(embedded_context_signature and not signatures_match),
                "similar_images": similar_images,
                "similar_found": len(similar_images) > 0
            }

            return jsonify(result)

        finally:
            # Nettoyer le fichier temporaire
            if os.path.exists(temp_filepath):
                os.remove(temp_filepath)

    except Exception as e:
        logger.error(f"Erreur vérification intégrité: {str(e)}")
        return jsonify({"error": f"Erreur lors de la vérification: {str(e)}"}), 500

@image_bp_v2.route('/images', methods=['GET'])
def list_images():
    """
    Endpoint pour lister toutes les images analysées.
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)

        images = ImageAnalysis.query.paginate(
            page=page, per_page=per_page, error_out=False
        )

        return jsonify({
            "images": [{
                "id": img.id,
                "filename": img.filename,
                "upload_timestamp": img.upload_timestamp.isoformat() if img.upload_timestamp else None,
                "has_steganography": img.has_steganography,
                "ai_confidence": img.ai_confidence,
                "image_url": f"/api/uploads/{os.path.basename(img.image_path)}" if img.image_path else None
            } for img in images.items],
            "pagination": {
                "page": images.page,
                "pages": images.pages,
                "per_page": images.per_page,
                "total": images.total
            }
        })

    except Exception as e:
        logger.error(f"Erreur listing images: {str(e)}")
        return jsonify({"error": f"Erreur lors du listing: {str(e)}"}), 500

@image_bp_v2.route('/uploads/<filename>')
def get_uploaded_file(filename):
    """Endpoint pour servir les fichiers uploadés."""
    try:
        return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
    except Exception as e:
        logger.error(f"Erreur récupération fichier: {str(e)}")
        return jsonify({"error": "Fichier non trouvé"}), 404

@image_bp_v2.route('/test', methods=['GET'])
def test_api():
    """Endpoint de test pour vérifier que l'API fonctionne."""
    try:
        ai_status = ai_service.is_available() if ai_service else {"error": "Service non initialisé"}

        return jsonify({
            "message": "API Images opérationnelle",
            "services": {
                "ai_detection": ai_status,
                "steganography": "Disponible",
                "image_processing": "Disponible"
            },
            "endpoints": [
                "/api/upload",
                "/api/add_steganography",
                "/api/verify_integrity",
                "/api/images",
                "/api/uploads/<filename>"
            ]
        })
    except Exception as e:
        logger.error(f"Erreur test API: {str(e)}")
        return jsonify({"error": f"Erreur test: {str(e)}"}), 500

def get_image_metadata(image_path):
    """
    Extrait les métadonnées d'une image.

    Args:
        image_path: Chemin vers l'image

    Returns:
        Dictionnaire avec les métadonnées
    """
    try:
        from PIL import Image
        img = Image.open(image_path)
        return {
            "dimensions": f"{img.width}x{img.height}",
            "format": img.format,
            "mode": img.mode,
            "size": f"{os.path.getsize(image_path) / 1024:.2f} KB"
        }
    except Exception as e:
        return {"error": f"Impossible d'extraire les métadonnées: {str(e)}"}

# Export du blueprint
__all__ = ['image_bp_v2']
