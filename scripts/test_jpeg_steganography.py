"""
Tests et exemples d'utilisation du service de stéganographie JPEG.
"""

import os
import sys
import logging
from pathlib import Path

# Ajouter le chemin parent pour importer le service
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.jpeg_steganography_service import JPEGSteganographyService

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_jpeg_steganography():
    """Test complet du service de stéganographie JPEG."""

    # Initialiser le service
    jpeg_service = JPEGSteganographyService()

    # Définir les chemins
    test_images_dir = Path(__file__).parent.parent.parent / "test_images"

    # Chercher une image JPEG de test
    jpeg_files = list(test_images_dir.glob("*.jpg")) + list(test_images_dir.glob("*.jpeg"))

    if not jpeg_files:
        logger.error("Aucune image JPEG trouvée dans test_images/")
        logger.info("Créez un fichier JPEG de test ou copiez-en un dans le dossier test_images/")
        return

    test_image = jpeg_files[0]
    logger.info(f"Utilisation de l'image de test: {test_image}")

    # Message de test
    test_message = "Ceci est un message secret caché dans l'image JPEG! 🔐"

    print("=" * 60)
    print("TEST DU SERVICE DE STÉGANOGRAPHIE JPEG")
    print("=" * 60)

    # 1. Analyser la capacité de l'image
    print("\n1. ANALYSE DE LA CAPACITÉ")
    print("-" * 30)
    capacity = jpeg_service.analyze_jpeg_capacity(str(test_image))
    if 'error' not in capacity:
        print(f"Dimensions: {capacity['image_dimensions']}")
        print(f"Taille fichier: {capacity['file_size']} bytes")
        print(f"Capacité LSB: {capacity['capacity_lsb_bytes']} bytes")
        print(f"Capacité EXIF: {capacity['capacity_exif_bytes']} bytes")
        print(f"Méthode recommandée: {capacity['recommended_method']}")
        print(f"Qualité estimée: {capacity['quality_estimate']}%")
    else:
        print(f"Erreur: {capacity['error']}")
        return

    # 2. Test de chaque méthode
    methods = ['exif', 'lsb']

    for method in methods:
        print(f"\n2. TEST MÉTHODE: {method.upper()}")
        print("-" * 30)

        # Définir le fichier de sortie
        output_file = test_images_dir / f"test_stego_{method}.jpg"

        # Cacher le message
        hide_result = jpeg_service.hide_message_in_jpeg(
            str(test_image),
            test_message,
            str(output_file),
            method=method
        )

        if hide_result['success']:
            print(f"✅ Message caché avec succès!")
            print(f"   Fichier de sortie: {output_file}")
            print(f"   Taille message: {hide_result['message_length']} caractères")

            # Extraire le message
            extract_result = jpeg_service.extract_message_from_jpeg(
                str(output_file),
                method=method
            )

            if extract_result['success'] and extract_result.get('message'):
                extracted_message = extract_result['message']
                print(f"✅ Message extrait: '{extracted_message}'")

                # Vérifier l'intégrité
                if extracted_message == test_message:
                    print("✅ Intégrité vérifiée: Message identique!")
                else:
                    print("❌ Erreur d'intégrité: Message différent!")
            else:
                print(f"❌ Échec de l'extraction: {extract_result.get('error', 'Aucun message trouvé')}")
        else:
            print(f"❌ Échec de la dissimulation: {hide_result.get('error')}")

    # 3. Test de la signature stéganographique
    print(f"\n3. TEST SIGNATURE STÉGANOGRAPHIQUE")
    print("-" * 40)

    signed_file = test_images_dir / "test_signed.jpg"

    # Créer une signature
    signature_result = jpeg_service.create_steganographic_signature(
        str(test_image),
        str(signed_file)
    )

    if signature_result.get('success'):
        print("✅ Signature créée avec succès!")
        print(f"   Hash de contenu: {signature_result['signature_data']['content_hash'][:16]}...")

        # Vérifier la signature
        verification_result = jpeg_service.verify_steganographic_signature(str(signed_file))

        if verification_result['verified']:
            print("✅ Signature vérifiée: Image intègre!")
        else:
            print(f"❌ Signature invalide: {verification_result.get('reason')}")
    else:
        print(f"❌ Échec création signature: {signature_result.get('error')}")

    print("\n" + "=" * 60)
    print("FIN DES TESTS")
    print("=" * 60)

def demo_usage():
    """Démonstration simple d'utilisation."""
    print("\nDÉMONSTRATION SIMPLE")
    print("=" * 40)

    service = JPEGSteganographyService()

    # Exemple de code d'utilisation
    code_example = '''
# Utilisation simple du service
from app.services.jpeg_steganography_service import JPEGSteganographyService

# Initialiser le service
jpeg_service = JPEGSteganographyService()

# Cacher un message
result = jpeg_service.hide_message_in_jpeg(
    "image_source.jpg",
    "Mon message secret",
    "image_avec_message.jpg",
    method="exif"  # ou "lsb"
)

# Extraire le message
extraction = jpeg_service.extract_message_from_jpeg(
    "image_avec_message.jpg",
    method="exif"
)

if extraction['success']:
    print("Message trouvé:", extraction['message'])

# Analyser la capacité
capacity = jpeg_service.analyze_jpeg_capacity("mon_image.jpg")
print("Capacité LSB:", capacity['capacity_lsb_bytes'], "bytes")
'''

    print(code_example)

if __name__ == "__main__":
    try:
        test_jpeg_steganography()
        demo_usage()
    except KeyboardInterrupt:
        print("\n\nTest interrompu par l'utilisateur.")
    except Exception as e:
        logger.error(f"Erreur durante les tests: {str(e)}")
        print(f"\nErreur: {str(e)}")
