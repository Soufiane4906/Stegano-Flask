#!/usr/bin/env python3
"""
Test complet de l'application Stegano-Flask avec TensorFlow
"""

import requests
import json
import os
import time
from datetime import datetime

BASE_URL = "http://localhost:5000"
TEST_IMAGE_PATH = "test_images/test_image_1.jpg"

def test_api_endpoints():
    """Test tous les endpoints de l'API."""

    print("=== Test des endpoints de base ===")

    # Test du health check
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check OK")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur health check: {e}")

    # Test de l'endpoint racine
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Root endpoint OK - Version: {data.get('version', 'N/A')}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur root endpoint: {e}")

    # Test des endpoints avancés (v2)
    try:
        response = requests.get(f"{BASE_URL}/api/v2/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API v2 health check OK")
            services = data.get('services', {})
            for service, status in services.items():
                status_icon = "✅" if status else "❌"
                print(f"  {status_icon} {service}: {status}")
        else:
            print(f"❌ API v2 health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur API v2 health check: {e}")

def test_steganography_endpoints():
    """Test des endpoints de stéganographie."""

    print("\n=== Test des endpoints de stéganographie ===")

    if not os.path.exists(TEST_IMAGE_PATH):
        print(f"❌ Image de test non trouvée: {TEST_IMAGE_PATH}")
        return

    # Test d'insertion de message (LSB custom)
    try:
        with open(TEST_IMAGE_PATH, 'rb') as f:
            files = {'image': f}
            data = {'message': 'Message de test secret'}

            response = requests.post(
                f"{BASE_URL}/api/v2/steganography/embed-custom",
                files=files,
                data=data
            )

            if response.status_code == 200:
                result = response.json()
                print("✅ Insertion LSB custom réussie")
                print(f"  Capacité utilisée: {result['result']['capacity_used']:.2f}%")
                return result.get('result', {}).get('output_path')
            else:
                print(f"❌ Insertion LSB custom échouée: {response.status_code}")
                print(f"  Erreur: {response.text}")

    except Exception as e:
        print(f"❌ Erreur test insertion: {e}")

    return None

def test_ai_detection():
    """Test de détection IA."""

    print("\n=== Test de détection IA ===")

    if not os.path.exists(TEST_IMAGE_PATH):
        print(f"❌ Image de test non trouvée: {TEST_IMAGE_PATH}")
        return

    try:
        with open(TEST_IMAGE_PATH, 'rb') as f:
            files = {'image': f}

            response = requests.post(
                f"{BASE_URL}/api/v2/ai/detect-generated",
                files=files
            )

            if response.status_code == 200:
                result = response.json()
                print("✅ Détection IA réussie")
                ai_result = result.get('result', {})
                if 'is_ai_generated' in ai_result:
                    print(f"  IA générée: {ai_result['is_ai_generated']}")
                    print(f"  Confiance: {ai_result.get('confidence', 0):.2f}")
                else:
                    print("  Modèle IA non disponible")
            else:
                print(f"❌ Détection IA échouée: {response.status_code}")
                print(f"  Erreur: {response.text}")

    except Exception as e:
        print(f"❌ Erreur test détection IA: {e}")

def test_similarity_analysis():
    """Test d'analyse de similarité."""

    print("\n=== Test d'analyse de similarité ===")

    if not os.path.exists(TEST_IMAGE_PATH):
        print(f"❌ Image de test non trouvée: {TEST_IMAGE_PATH}")
        return

    try:
        with open(TEST_IMAGE_PATH, 'rb') as f:
            files = {'image': f}

            response = requests.post(
                f"{BASE_URL}/api/v2/analysis/similarity",
                files=files
            )

            if response.status_code == 200:
                result = response.json()
                print("✅ Analyse de similarité réussie")
                print(f"  Images similaires trouvées: {result['total_found']}")

                hashes = result.get('hashes', {})
                if hashes.get('success'):
                    print(f"  pHash: {hashes.get('phash', 'N/A')}")
                    print(f"  dHash: {hashes.get('dhash', 'N/A')}")
            else:
                print(f"❌ Analyse de similarité échouée: {response.status_code}")
                print(f"  Erreur: {response.text}")

    except Exception as e:
        print(f"❌ Erreur test similarité: {e}")

def test_structure_analysis():
    """Test d'analyse de structure."""

    print("\n=== Test d'analyse de structure ===")

    if not os.path.exists(TEST_IMAGE_PATH):
        print(f"❌ Image de test non trouvée: {TEST_IMAGE_PATH}")
        return

    try:
        with open(TEST_IMAGE_PATH, 'rb') as f:
            files = {'image': f}

            response = requests.post(
                f"{BASE_URL}/api/v2/analysis/structure",
                files=files
            )

            if response.status_code == 200:
                result = response.json()
                print("✅ Analyse de structure réussie")
                analysis = result.get('analysis', {})
                if 'statistics' in analysis:
                    stats = analysis['statistics']
                    print(f"  Score de suspicion: {analysis.get('suspicion_score', 0):.2f}")
                    print(f"  Stéganographie probable: {analysis.get('analysis', {}).get('likely_steganography', False)}")
            else:
                print(f"❌ Analyse de structure échouée: {response.status_code}")
                print(f"  Erreur: {response.text}")

    except Exception as e:
        print(f"❌ Erreur test structure: {e}")

def main():
    """Fonction principale de test."""
    print("🧪 Test complet de l'API Stegano-Flask")
    print(f"⏰ Démarré à: {datetime.now().isoformat()}")
    print(f"🌐 URL de base: {BASE_URL}")
    print()

    # Attendre que le serveur soit prêt
    print("⏳ Attente du démarrage du serveur...")
    time.sleep(2)

    # Tests séquentiels
    test_api_endpoints()
    test_steganography_endpoints()
    test_ai_detection()
    test_similarity_analysis()
    test_structure_analysis()

    print("\n✅ Tests terminés")

if __name__ == "__main__":
    main()
