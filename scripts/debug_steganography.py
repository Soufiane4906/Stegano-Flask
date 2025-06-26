#!/usr/bin/env python3
"""
Test rapide du service de stéganographie pour diagnostiquer le problème.
"""

import os
import sys
from PIL import Image

# Ajouter le répertoire du projet au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_steganography_debug():
    """Test détaillé de la stéganographie."""
    print("🔍 Test de diagnostic de la stéganographie")
    print("=" * 50)

    try:
        from app.services.steganography_service import SteganographyService

        # Créer une image de test
        test_image_path = "debug_test.png"
        test_image = Image.new('RGB', (256, 256), color='blue')
        test_image.save(test_image_path)

        try:
            # Test 1: Cacher un message
            print("📝 Test 1: Cacher un message...")
            message = "Test message secret pour debug"
            result_path = SteganographyService.embed_message(test_image_path, message)
            print(f"✅ Message caché dans: {result_path}")
            print(f"📁 Fichier existe: {os.path.exists(result_path)}")

            # Test 2: Révéler le message
            print("\n🔍 Test 2: Révéler le message...")
            revealed = SteganographyService.detect_hidden_message(result_path)
            print(f"📊 Résultat brut: {revealed}")

            if 'signature_detected' in revealed:
                if revealed['signature_detected']:
                    print(f"✅ Message trouvé: '{revealed.get('signature', 'VIDE')}'")
                    return True
                else:
                    print("❌ Aucun message détecté")
                    return False
            else:
                print(f"❌ Format de retour incorrect: {revealed}")
                return False

        finally:
            # Nettoyer
            for path in [test_image_path, test_image_path.replace('.', '_steg.')]:
                if os.path.exists(path):
                    os.remove(path)
                    print(f"🗑️ Supprimé: {path}")

    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_with_uploaded_image():
    """Test avec l'image uploadée mentionnée."""
    print("\n🖼️ Test avec l'image spécifique")
    print("=" * 50)

    # L'image mentionnée dans le problème
    image_path = "uploads/8fffe33e-1b5a-49aa-9efa-cab162d7cdc2_steg.png"

    if not os.path.exists(image_path):
        print(f"❌ Image non trouvée: {image_path}")
        # Chercher dans les autres dossiers
        possible_paths = [
            "test_uploads/8fffe33e-1b5a-49aa-9efa-cab162d7cdc2_steg.png",
            "8fffe33e-1b5a-49aa-9efa-cab162d7cdc2_steg.png"
        ]

        for path in possible_paths:
            if os.path.exists(path):
                image_path = path
                print(f"✅ Image trouvée: {image_path}")
                break
        else:
            print("❌ Image introuvable dans tous les emplacements")
            return False

    try:
        from app.services.steganography_service import SteganographyService

        print(f"🔍 Analyse de: {image_path}")
        result = SteganographyService.detect_hidden_message(image_path)
        print(f"📊 Résultat: {result}")

        if result.get('signature_detected'):
            print(f"✅ Message trouvé: '{result.get('signature')}'")
        else:
            print("❌ Aucun message trouvé")

        return result.get('signature_detected', False)

    except Exception as e:
        print(f"❌ Erreur lors de l'analyse: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Diagnostic de stéganographie")
    print("=" * 60)

    # Test 1: Test général
    success1 = test_steganography_debug()

    # Test 2: Test avec l'image spécifique
    success2 = test_with_uploaded_image()

    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ")
    print("=" * 60)
    print(f"Test général: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"Test image spécifique: {'✅ PASS' if success2 else '❌ FAIL'}")

    if success1 and not success2:
        print("\n💡 DIAGNOSTIC:")
        print("- Le service de stéganographie fonctionne")
        print("- L'image spécifique ne contient peut-être pas de message")
        print("- Ou l'image a été corrompue/modifiée")
    elif not success1:
        print("\n💡 DIAGNOSTIC:")
        print("- Problème avec le service de stéganographie")
        print("- Vérifiez l'installation de la bibliothèque 'stegano'")
