#!/usr/bin/env python3
"""
Test complet des services mis à jour - Refactoring final
Vérifie que tous les services utilisent la logique exacte de steganoV2.py
"""

import os
import requests
import json
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:5000"
TEST_IMAGE_DIR = "test_images"

def test_steganography_endpoints():
    """Test les endpoints de stéganographie (logique LSB de steganoV2.py)."""
    print("\n🔍 Test des endpoints de stéganographie...")

    test_image = os.path.join(TEST_IMAGE_DIR, "test_image_1.png")
    if not os.path.exists(test_image):
        print(f"❌ Image de test non trouvée: {test_image}")
        return False

    message = "Test message from final refactoring"

    try:
        # Test hide message (embed_steganography logic)
        print("📤 Test hide message...")
        with open(test_image, 'rb') as f:
            response = requests.post(
                f"{BASE_URL}/api/images/hide",
                files={'file': f},
                data={'message': message}
            )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Message caché avec succès: {result.get('data', {}).get('output_path', 'N/A')}")
            hidden_image_path = result.get('data', {}).get('output_path')

            # Test reveal message (analyze_steganography logic)
            if hidden_image_path and os.path.exists(hidden_image_path):
                print("📥 Test reveal message...")
                with open(hidden_image_path, 'rb') as f:
                    response = requests.post(
                        f"{BASE_URL}/api/images/reveal",
                        files={'file': f}
                    )

                if response.status_code == 200:
                    reveal_result = response.json()
                    revealed_message = reveal_result.get('data', {}).get('steganography', {}).get('signature')
                    if revealed_message == message:
                        print(f"✅ Message révélé correctement: '{revealed_message}'")
                        return True
                    else:
                        print(f"❌ Message révélé incorrect. Attendu: '{message}', Reçu: '{revealed_message}'")
                else:
                    print(f"❌ Erreur reveal: {response.status_code} - {response.text}")
            else:
                print("❌ Image cachée non trouvée pour le test reveal")
        else:
            print(f"❌ Erreur hide: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"❌ Erreur lors du test stéganographie: {e}")

    return False

def test_ai_detection_endpoint():
    """Test l'endpoint de détection IA (logique model.h5 de steganoV2.py)."""
    print("\n🤖 Test de l'endpoint de détection IA...")

    test_image = os.path.join(TEST_IMAGE_DIR, "test_image_1.png")
    if not os.path.exists(test_image):
        print(f"❌ Image de test non trouvée: {test_image}")
        return False

    try:
        with open(test_image, 'rb') as f:
            response = requests.post(
                f"{BASE_URL}/api/images/ai-detection",
                files={'file': f}
            )

        if response.status_code == 200:
            result = response.json()
            ai_data = result.get('data', {}).get('ai_detection', {})

            # Vérifier la structure de réponse de steganoV2.py
            if 'is_ai_generated' in ai_data and 'confidence' in ai_data and 'model_used' in ai_data:
                print(f"✅ Détection IA réussie:")
                print(f"   - IA générée: {ai_data['is_ai_generated']}")
                print(f"   - Confiance: {ai_data['confidence']:.2f}")
                print(f"   - Modèle: {ai_data['model_used']}")
                return True
            else:
                print(f"❌ Structure de réponse incorrecte: {ai_data}")
        else:
            print(f"❌ Erreur détection IA: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"❌ Erreur lors du test détection IA: {e}")

    return False

def test_similarity_endpoint():
    """Test l'endpoint de similarité (logique hash/hamming de steganoV2.py)."""
    print("\n🔍 Test de l'endpoint de similarité...")

    test_image1 = os.path.join(TEST_IMAGE_DIR, "test_image_1.png")
    test_image2 = os.path.join(TEST_IMAGE_DIR, "test_image_2.png")

    if not os.path.exists(test_image1) or not os.path.exists(test_image2):
        print(f"❌ Images de test non trouvées: {test_image1}, {test_image2}")
        return False

    try:
        with open(test_image1, 'rb') as f1, open(test_image2, 'rb') as f2:
            response = requests.post(
                f"{BASE_URL}/api/images/similarity",
                files={'file1': f1, 'file2': f2}
            )

        if response.status_code == 200:
            result = response.json()

            # Vérifier la structure de réponse de steganoV2.py
            if 'similarity' in result and 'method' in result:
                similarity = result.get('similarity', {})
                if 'phash' in similarity and 'dhash' in similarity and 'average' in similarity:
                    print(f"✅ Comparaison de similarité réussie:")
                    print(f"   - pHash: {similarity['phash']:.2f}%")
                    print(f"   - dHash: {similarity['dhash']:.2f}%")
                    print(f"   - Moyenne: {similarity['average']:.2f}%")
                    print(f"   - Méthode: {result['method']}")
                    return True
                else:
                    print(f"❌ Structure de similarité incorrecte: {similarity}")
            else:
                print(f"❌ Structure de réponse incorrecte: {result}")
        else:
            print(f"❌ Erreur comparaison: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"❌ Erreur lors du test similarité: {e}")

    return False

def test_complete_analysis():
    """Test l'analyse complète d'une image."""
    print("\n📊 Test de l'analyse complète...")

    test_image = os.path.join(TEST_IMAGE_DIR, "test_image_1.png")
    if not os.path.exists(test_image):
        print(f"❌ Image de test non trouvée: {test_image}")
        return False

    try:
        with open(test_image, 'rb') as f:
            response = requests.post(
                f"{BASE_URL}/api/images/upload",
                files={'file': f}
            )

        if response.status_code == 200:
            result = response.json()
            data = result.get('data', {})

            # Vérifier que tous les composants sont présents
            required_keys = ['steganography', 'ai_detection', 'metadata', 'similar_images']
            missing_keys = [key for key in required_keys if key not in data]

            if not missing_keys:
                print("✅ Analyse complète réussie:")
                print(f"   - Stéganographie: {data['steganography'].get('signature_detected', 'N/A')}")
                print(f"   - IA générée: {data['ai_detection'].get('is_ai_generated', 'N/A')}")
                print(f"   - Métadonnées: {data['metadata'].get('dimensions', 'N/A')}")
                print(f"   - Images similaires: {len(data.get('similar_images', []))}")
                return True
            else:
                print(f"❌ Clés manquantes dans l'analyse: {missing_keys}")
        else:
            print(f"❌ Erreur analyse complète: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"❌ Erreur lors de l'analyse complète: {e}")

    return False

def check_server_status():
    """Vérifie que le serveur est en cours d'exécution."""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    print("🚀 Test final des services refactorisés - Logique steganoV2.py")
    print("=" * 60)

    # Vérifier que le serveur est en cours d'exécution
    if not check_server_status():
        print("❌ Serveur Flask non accessible. Assurez-vous qu'il est démarré sur http://localhost:5000")
        return

    print("✅ Serveur Flask accessible")

    # Créer le dossier d'images de test s'il n'existe pas
    os.makedirs(TEST_IMAGE_DIR, exist_ok=True)

    # Exécuter tous les tests
    tests = [
        ("Stéganographie (LSB)", test_steganography_endpoints),
        ("Détection IA (model.h5)", test_ai_detection_endpoint),
        ("Similarité (Hash/Hamming)", test_similarity_endpoint),
        ("Analyse complète", test_complete_analysis),
    ]

    results = []
    for test_name, test_func in tests:
        success = test_func()
        results.append((test_name, success))

    # Résumé des résultats
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 60)

    passed = 0
    for test_name, success in results:
        status = "✅ PASSÉ" if success else "❌ ÉCHOUÉ"
        print(f"{test_name}: {status}")
        if success:
            passed += 1

    print(f"\n🎯 Résultat final: {passed}/{len(results)} tests réussis")

    if passed == len(results):
        print("🎉 TOUS LES TESTS SONT PASSÉS ! Le refactoring est terminé avec succès.")
        print("📌 Les services utilisent maintenant exactement la logique de steganoV2.py")
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")

if __name__ == "__main__":
    main()
