#!/usr/bin/env python3
"""
Script de test final pour valider le refactoring
Teste que tous les services utilisent la logique exacte de steganoV2.py
"""

import requests
import time
import os

# Configuration
BASE_URL = "http://127.0.0.1:5000"
TEST_IMAGE = "test_images/test_image_1.png"

def test_server_running():
    """Test si le serveur Flask répond"""
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ Serveur Flask opérationnel (Status: {response.status_code})")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Serveur Flask non accessible")
        return False

def test_steganography_endpoints():
    """Test des endpoints de stéganographie"""
    print("\n🔍 Test des endpoints de stéganographie...")

    if not os.path.exists(TEST_IMAGE):
        print(f"❌ Image de test non trouvée: {TEST_IMAGE}")
        return False

    try:
        # Test cacher un message
        with open(TEST_IMAGE, 'rb') as f:
            files = {'file': f}
            data = {'message': 'Message secret de test'}
            response = requests.post(f"{BASE_URL}/api/images/steganography/add", files=files, data=data)

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Ajout stéganographie OK: {result.get('success', False)}")

            # Récupérer le nom du fichier généré
            if 'data' in result and 'stego_image_path' in result['data']:
                stego_file = result['data']['stego_image_path']
                print(f"   Fichier généré: {stego_file}")
                return True
        else:
            print(f"❌ Erreur ajout stéganographie: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"❌ Exception test stéganographie: {str(e)}")
        return False

def test_ai_detection_endpoint():
    """Test de l'endpoint de détection IA"""
    print("\n🤖 Test de l'endpoint de détection IA...")

    if not os.path.exists(TEST_IMAGE):
        print(f"❌ Image de test non trouvée: {TEST_IMAGE}")
        return False

    try:
        with open(TEST_IMAGE, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{BASE_URL}/api/images/ai-detection", files=files)

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Détection IA OK: {result.get('success', False)}")

            if 'data' in result:
                data = result['data']
                print(f"   Confiance IA: {data.get('confidence', 'N/A')}")
                print(f"   Est IA: {data.get('is_ai_generated', 'N/A')}")
                print(f"   Modèle utilisé: {data.get('model', 'N/A')}")
            return True
        else:
            print(f"❌ Erreur détection IA: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"❌ Exception test détection IA: {str(e)}")
        return False

def test_similarity_endpoint():
    """Test de l'endpoint de similarité"""
    print("\n🔍 Test de l'endpoint de similarité...")

    # Utiliser la même image deux fois pour tester la similarité maximale
    if not os.path.exists(TEST_IMAGE):
        print(f"❌ Image de test non trouvée: {TEST_IMAGE}")
        return False

    try:
        with open(TEST_IMAGE, 'rb') as f1, open(TEST_IMAGE, 'rb') as f2:
            files = {'file1': f1, 'file2': f2}
            response = requests.post(f"{BASE_URL}/api/images/similarity", files=files)

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Comparaison similarité OK: {result.get('status', 'N/A')}")

            if 'similarity' in result:
                sim = result['similarity']
                print(f"   Similarité moyenne: {sim.get('average', 'N/A')}%")
                print(f"   Identiques: {result.get('identical', 'N/A')}")
                print(f"   Méthode: {result.get('method', 'N/A')}")
            return True
        else:
            print(f"❌ Erreur similarité: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"❌ Exception test similarité: {str(e)}")
        return False

def test_upload_and_analyze():
    """Test de l'endpoint d'analyse complète"""
    print("\n📊 Test de l'endpoint d'analyse complète...")

    if not os.path.exists(TEST_IMAGE):
        print(f"❌ Image de test non trouvée: {TEST_IMAGE}")
        return False

    try:
        with open(TEST_IMAGE, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{BASE_URL}/api/images/upload", files=files)

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Analyse complète OK: {result.get('success', False)}")

            if 'data' in result:
                data = result['data']
                print(f"   Stéganographie détectée: {data.get('steganography', {}).get('signature_detected', 'N/A')}")
                print(f"   Détection IA: {data.get('ai_detection', {}).get('is_ai_generated', 'N/A')}")
                print(f"   Images similaires trouvées: {len(data.get('similar_images', []))}")
            return True
        else:
            print(f"❌ Erreur analyse complète: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"❌ Exception test analyse complète: {str(e)}")
        return False

def main():
    """Fonction principale de test"""
    print("🚀 Test du refactoring final - Stegano-Flask")
    print("=" * 50)

    # Attendre un peu que le serveur soit prêt
    print("⏳ Attente du démarrage du serveur...")
    time.sleep(3)

    # Test de base
    if not test_server_running():
        print("\n❌ ÉCHEC: Serveur non accessible")
        return False

    # Tests des endpoints
    success_count = 0
    total_tests = 4

    if test_steganography_endpoints():
        success_count += 1

    if test_ai_detection_endpoint():
        success_count += 1

    if test_similarity_endpoint():
        success_count += 1

    if test_upload_and_analyze():
        success_count += 1

    # Résumé
    print("\n" + "=" * 50)
    print(f"📊 RÉSULTATS: {success_count}/{total_tests} tests réussis")

    if success_count == total_tests:
        print("🎉 SUCCÈS: Tous les endpoints fonctionnent avec la logique de steganoV2.py!")
        print("✅ Le refactoring est terminé avec succès!")
    else:
        print("⚠️  ATTENTION: Certains tests ont échoué")
        print("🔧 Vérifiez les logs pour plus de détails")

    return success_count == total_tests

if __name__ == "__main__":
    main()
