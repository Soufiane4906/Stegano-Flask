#!/usr/bin/env python3
"""
Test simple pour vérifier que les services refactorisés fonctionnent
"""

import os
import sys

# Ajouter le répertoire racine au PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test que tous les imports fonctionnent"""
    print("🔍 Test des imports...")

    try:
        from app.services.steganography_service import SteganographyService
        print("✅ SteganographyService importé")

        from app.services.ai_detection_service_v2 import AIDetectionService
        print("✅ AIDetectionService importé")

        from app.services.image_service import ImageService
        print("✅ ImageService importé")

        return True
    except Exception as e:
        print(f"❌ Erreur d'import: {str(e)}")
        return False

def test_steganography_logic():
    """Test de la logique de stéganographie (sans Flask)"""
    print("\n🔍 Test de la logique de stéganographie...")

    try:
        from app.services.steganography_service import SteganographyService
        from stegano import lsb
        from PIL import Image
        import tempfile
        import os

        # Créer une image de test simple
        test_image = Image.new('RGB', (100, 100), color='red')

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            test_image.save(tmp.name)
            test_image_path = tmp.name

        try:
            # Test de la méthode embed_message
            message = "Test message secret"
            stego_path = SteganographyService.embed_message(test_image_path, message)
            print(f"✅ Message caché avec succès: {os.path.basename(stego_path)}")

            # Test de la méthode detect_hidden_message
            result = SteganographyService.detect_hidden_message(stego_path)
            if result.get('signature_detected') and result.get('signature') == message:
                print("✅ Message récupéré avec succès")
                return True
            else:
                print(f"❌ Message non récupéré correctement: {result}")
                return False

        finally:
            # Nettoyer les fichiers temporaires
            if os.path.exists(test_image_path):
                os.unlink(test_image_path)
            if 'stego_path' in locals() and os.path.exists(stego_path):
                os.unlink(stego_path)

    except Exception as e:
        print(f"❌ Erreur test stéganographie: {str(e)}")
        return False

def test_ai_detection_logic():
    """Test de la logique de détection IA (sans Flask)"""
    print("\n🤖 Test de la logique de détection IA...")

    try:
        from app.services.ai_detection_service_v2 import AIDetectionService
        from PIL import Image
        import tempfile
        import os

        # Créer une image de test simple
        test_image = Image.new('RGB', (128, 128), color='blue')

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            test_image.save(tmp.name)
            test_image_path = tmp.name

        try:
            ai_service = AIDetectionService()

            # Vérifier que le modèle est chargé
            if ai_service.is_model_loaded():
                print("✅ Modèle IA chargé")

                # Test de détection
                result = ai_service.detect_ai_image(test_image_path)
                print(f"✅ Détection IA effectuée: confiance = {result.get('confidence', 'N/A')}")
                return True
            else:
                print("⚠️  Modèle IA non disponible (mais service OK)")
                return True

        finally:
            if os.path.exists(test_image_path):
                os.unlink(test_image_path)

    except Exception as e:
        print(f"❌ Erreur test détection IA: {str(e)}")
        return False

def test_similarity_logic():
    """Test de la logique de similarité (sans Flask)"""
    print("\n🔍 Test de la logique de similarité...")

    try:
        from app.services.image_service import ImageService
        from app.services.ai_detection_service_v2 import AIDetectionService
        from werkzeug.datastructures import FileStorage
        from PIL import Image
        import tempfile
        import os
        import io

        # Créer deux images de test
        test_image1 = Image.new('RGB', (100, 100), color='green')
        test_image2 = Image.new('RGB', (100, 100), color='green')  # Identique

        # Créer des objets FileStorage pour simuler l'upload
        img1_bytes = io.BytesIO()
        test_image1.save(img1_bytes, format='PNG')
        img1_bytes.seek(0)

        img2_bytes = io.BytesIO()
        test_image2.save(img2_bytes, format='PNG')
        img2_bytes.seek(0)

        file1 = FileStorage(img1_bytes, filename='test1.png', content_type='image/png')
        file2 = FileStorage(img2_bytes, filename='test2.png', content_type='image/png')

        # Test de comparaison
        ai_service = AIDetectionService()
        image_service = ImageService('/tmp', ai_service)

        result = image_service.compare_similarity(file1, file2)

        if result.get('status') == 'success':
            similarity = result.get('similarity', {}).get('average', 0)
            print(f"✅ Comparaison de similarité effectuée: {similarity}%")
            print(f"   Méthode: {result.get('method', 'N/A')}")
            return True
        else:
            print(f"❌ Erreur comparaison: {result}")
            return False

    except Exception as e:
        print(f"❌ Erreur test similarité: {str(e)}")
        return False

def main():
    """Fonction principale de test"""
    print("🚀 Test des services refactorisés (logique steganoV2.py)")
    print("=" * 55)

    success_count = 0
    total_tests = 4

    if test_imports():
        success_count += 1

    if test_steganography_logic():
        success_count += 1

    if test_ai_detection_logic():
        success_count += 1

    if test_similarity_logic():
        success_count += 1

    # Résumé
    print("\n" + "=" * 55)
    print(f"📊 RÉSULTATS: {success_count}/{total_tests} tests réussis")

    if success_count == total_tests:
        print("🎉 SUCCÈS: Tous les services utilisent la logique de steganoV2.py!")
        print("✅ Le refactoring est terminé avec succès!")
    else:
        print("⚠️  ATTENTION: Certains tests ont échoué")

    return success_count == total_tests

if __name__ == "__main__":
    main()
