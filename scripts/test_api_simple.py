#!/usr/bin/env python3
"""
Script de test rapide pour vérifier que l'application fonctionne.
"""

import requests
import json

def test_api():
    """Test simple de l'API."""
    base_url = "http://localhost:5000"

    print("🧪 Test de l'API Stégano-Flask")
    print("=" * 50)

    # Test 1: Vérification de l'endpoint racine
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ GET / : {response.status_code}")
        print(f"   Réponse: {response.json()}")
    except Exception as e:
        print(f"❌ GET / : Erreur - {e}")

    # Test 2: Vérification de l'endpoint de test
    try:
        response = requests.get(f"{base_url}/api/test")
        print(f"✅ GET /api/test : {response.status_code}")
        print(f"   Réponse: {response.json()}")
    except Exception as e:
        print(f"❌ GET /api/test : Erreur - {e}")

    # Test 3: Vérification de l'endpoint health
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ GET /health : {response.status_code}")
        print(f"   Réponse: {response.json()}")
    except Exception as e:
        print(f"❌ GET /health : Erreur - {e}")

    # Test 4: Vérification de l'endpoint v2
    try:
        response = requests.get(f"{base_url}/api/v2/test")
        print(f"✅ GET /api/v2/test : {response.status_code}")
        print(f"   Réponse: {response.json()}")
    except Exception as e:
        print(f"❌ GET /api/v2/test : Erreur - {e}")

if __name__ == "__main__":
    test_api()
