#!/usr/bin/env python3
"""
Script de test pour vérifier que l'application fonctionne correctement
"""

import requests
import time
import sys

def test_endpoints():
    """Test tous les endpoints de l'application"""
    base_url = "http://localhost:5000"

    tests = [
        ("GET", "/", "Page d'accueil"),
        ("GET", "/health", "Health check"),
        ("GET", "/api/status", "API status"),
        ("GET", "/api/test", "API test"),
        ("GET", "/steganography.html", "Page stéganographie"),
        ("GET", "/ai-detection.html", "Page détection IA"),
        ("GET", "/similarity.html", "Page similarité"),
        ("GET", "/test-api.html", "Page test API"),
        ("GET", "/simple-test", "Test simple"),
        ("GET", "/test-templates", "Test templates"),
    ]

    print("🔍 Test des endpoints...")
    print("=" * 50)

    for method, endpoint, description in tests:
        try:
            url = f"{base_url}{endpoint}"
            response = requests.get(url, timeout=5)

            status = "✅ OK" if response.status_code == 200 else f"❌ {response.status_code}"
            print(f"{description:<25} {endpoint:<20} {status}")

        except requests.exceptions.ConnectionError:
            print(f"{description:<25} {endpoint:<20} ❌ CONNEXION REFUSÉE")
        except Exception as e:
            print(f"{description:<25} {endpoint:<20} ❌ {str(e)}")

    print("=" * 50)

if __name__ == "__main__":
    print("🚀 Démarrage des tests...")
    print("💡 Assurez-vous que l'application est démarrée avec 'python run.py'")
    print()

    # Attendre un peu pour que l'utilisateur démarre l'app
    time.sleep(2)

    test_endpoints()

    print("\n✨ Tests terminés !")
    print("📝 Si des endpoints échouent, vérifiez les logs de l'application.")
