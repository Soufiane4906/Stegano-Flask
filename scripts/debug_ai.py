#!/usr/bin/env python3
"""
Script de debug pour tester le service de détection IA
"""

import sys
import os

# Ajouter le répertoire racine au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_ai_detection_service():
    """Test du service de détection IA"""

    print("🔍 Test du service de détection IA...")

    try:
        # Importer le service
        from app.services.ai_detection_service_v2 import AIDetectionService
        print("✅ Import du service réussi")

        # Créer une instance
        ai_service = AIDetectionService()
        print("✅ Création de l'instance réussie")

        # Vérifier que TensorFlow est disponible
        try:
            import tensorflow as tf
            print(f"✅ TensorFlow version: {tf.__version__}")
        except ImportError:
            print("❌ TensorFlow non disponible")
            return

        # Chercher une image de test
        test_images_dir = "test_images"
        if not os.path.exists(test_images_dir):
            print(f"❌ Dossier {test_images_dir} manquant")
            return

        test_image = None
        for file in os.listdir(test_images_dir):
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                test_image = os.path.join(test_images_dir, file)
                break

        if not test_image:
            print("❌ Aucune image de test trouvée")
            return

        print(f"📸 Image de test: {test_image}")

        # Tester la détection
        result = ai_service.detect_ai_generated(test_image)
        print(f"✅ Détection réussie: {result}")

    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

def test_image_service():
    """Test du service d'images complet"""

    print("\n🔍 Test du service d'images...")

    try:
        from app.services.image_service import ImageService
        from app.services.ai_detection_service_v2 import AIDetectionService

        # Créer les services
        ai_service = AIDetectionService()
        image_service = ImageService("uploads", ai_service)

        print("✅ Services créés avec succès")

        # Tester l'accès aux méthodes
        print(f"✅ ai_service disponible: {hasattr(image_service, 'ai_service')}")
        print(f"✅ detect_ai_generated disponible: {hasattr(image_service.ai_service, 'detect_ai_generated')}")

    except Exception as e:
        print(f"❌ Erreur service d'images: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Debug des services de détection IA")
    print("=" * 50)

    test_ai_detection_service()
    test_image_service()

    print("\n" + "=" * 50)
    print("✨ Tests terminés")
