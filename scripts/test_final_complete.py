#!/usr/bin/env python3
"""
Test du nouveau modèle IA et des services refactorisés.
"""

import os
import sys
import numpy as np
from PIL import Image

# Ajouter le répertoire du projet au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_ai_model_loading():
    """Test du chargement du nouveau modèle IA."""
    print("🤖 Test du chargement du modèle IA...")

    try:
        from app.services.ai_detection_service_v2 import AIDetectionService

        # Initialiser le service
        ai_service = AIDetectionService()

        # Vérifier le statut
        status = ai_service.is_available()
        print(f"📊 Statut du service IA: {status}")

        if ai_service.is_model_loaded():
            print("✅ Modèle IA chargé avec succès!")
            return True
        else:
            print("❌ Modèle IA non chargé")
            return False

    except Exception as e:
        print(f"❌ Erreur lors du test du modèle: {e}")
        return False

def test_ai_detection():
    """Test de la détection IA sur une image de test."""
    print("\n🔍 Test de la détection IA...")

    try:
        from app.services.ai_detection_service_v2 import AIDetectionService

        # Initialiser le service
        ai_service = AIDetectionService()

        if not ai_service.is_model_loaded():
            print("❌ Modèle non chargé, impossible de tester")
            return False

        # Créer une image de test
        test_image_path = "test_image_temp.png"
        test_image = Image.new('RGB', (128, 128), color='blue')
        test_image.save(test_image_path)

        try:
            # Tester la détection
            result = ai_service.detect_ai_image(test_image_path)
            print(f"📊 Résultat détection IA: {result}")

            # Vérifier que le résultat contient les bonnes clés
            required_keys = ['is_ai_generated', 'confidence']
            if all(key in result for key in required_keys):
                print("✅ Détection IA fonctionnelle!")
                return True
            else:
                print(f"❌ Résultat incomplet: {result}")
                return False

        finally:
            # Nettoyer
            if os.path.exists(test_image_path):
                os.remove(test_image_path)

    except Exception as e:
        print(f"❌ Erreur lors du test de détection: {e}")
        return False

def test_steganography_service():
    """Test du service de stéganographie."""
    print("\n🔐 Test du service de stéganographie...")

    try:
        from app.services.steganography_service import SteganographyService

        # Créer une image de test
        test_image_path = "test_stego_temp.png"
        test_image = Image.new('RGB', (256, 256), color='red')
        test_image.save(test_image_path)

        try:
            # Test d'intégration de message
            message = "Test message secret"
            result_path = SteganographyService.embed_message(test_image_path, message)
            print(f"📁 Image avec message créée: {result_path}")

            # Test de révélation de message
            revealed = SteganographyService.detect_hidden_message(result_path)
            print(f"🔍 Message révélé: {revealed}")

            if revealed.get('signature_detected') and revealed.get('signature') == message:
                print("✅ Stéganographie fonctionnelle!")
                return True
            else:
                print(f"❌ Échec stéganographie: {revealed}")
                return False

        finally:
            # Nettoyer
            for path in [test_image_path, test_image_path.replace('.', '_steg.')]:
                if os.path.exists(path):
                    os.remove(path)

    except Exception as e:
        print(f"❌ Erreur lors du test de stéganographie: {e}")
        return False

def test_image_similarity():
    """Test du service de similarité d'images."""
    print("\n🖼️ Test du service de similarité...")

    try:
        from app.services.image_service import ImageService
        from app.services.ai_detection_service_v2 import AIDetectionService
        from werkzeug.datastructures import FileStorage
        import io

        # Initialiser les services
        ai_service = AIDetectionService()
        image_service = ImageService("uploads", ai_service)

        # Créer deux images similaires
        img1 = Image.new('RGB', (128, 128), color='green')
        img2 = Image.new('RGB', (128, 128), color='green')

        # Convertir en FileStorage
        img1_bytes = io.BytesIO()
        img1.save(img1_bytes, format='PNG')
        img1_bytes.seek(0)
        file1 = FileStorage(img1_bytes, filename='test1.png', content_type='image/png')

        img2_bytes = io.BytesIO()
        img2.save(img2_bytes, format='PNG')
        img2_bytes.seek(0)
        file2 = FileStorage(img2_bytes, filename='test2.png', content_type='image/png')

        # Tester la comparaison
        result = image_service.compare_similarity(file1, file2)
        print(f"📊 Résultat similarité: {result}")

        if 'similarity' in result and 'average' in result['similarity']:
            print("✅ Service de similarité fonctionnel!")
            return True
        else:
            print(f"❌ Échec similarité: {result}")
            return False

    except Exception as e:
        print(f"❌ Erreur lors du test de similarité: {e}")
        return False

def main():
    """Fonction principale de test."""
    print("🧪 Test complet des services refactorisés")
    print("=" * 50)

    tests = [
        ("Chargement modèle IA", test_ai_model_loading),
        ("Détection IA", test_ai_detection),
        ("Stéganographie", test_steganography_service),
        ("Similarité d'images", test_image_similarity)
    ]

    results = []

    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Erreur critique dans {test_name}: {e}")
            results.append((test_name, False))

    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 50)

    passed = 0
    total = len(results)

    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if success:
            passed += 1

    print(f"\n📈 Résultat: {passed}/{total} tests réussis")

    if passed == total:
        print("🎉 Tous les tests sont passés! Le refactoring est réussi.")
        return True
    else:
        print("⚠️ Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
