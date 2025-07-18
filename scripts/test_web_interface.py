#!/usr/bin/env python3
"""
Script de test rapide pour vérifier que l'interface web fonctionne.

Ce script teste les endpoints de base de l'interface de test
sans avoir besoin de navigateur.
"""

import requests
import json
import sys
import os

def test_interface_endpoints(base_url="http://localhost:5000"):
    """Teste les endpoints de l'interface."""

    print("🧪 Test de l'interface web - JPEG Stéganographie")
    print("=" * 55)

    endpoints = [
        ("/test/status", "GET", "Statut de l'interface"),
        ("/test/files", "GET", "Liste des fichiers"),
        ("/test/help", "GET", "Aide de l'interface"),
        ("/api/v2/jpeg/methods", "GET", "Méthodes API")
    ]

    results = []

    for endpoint, method, description in endpoints:
        url = f"{base_url}{endpoint}"
        print(f"\n🔍 Test: {description}")
        print(f"   URL: {url}")

        try:
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                print(f"   ✅ {response.status_code} - OK")

                # Afficher un aperçu de la réponse pour l'API
                if endpoint.startswith("/api/"):
                    try:
                        data = response.json()
                        if "methods" in data:
                            methods = list(data["methods"].keys())
                            print(f"   📊 Méthodes disponibles: {', '.join(methods)}")
                    except:
                        pass

                elif endpoint == "/test/status":
                    try:
                        data = response.json()
                        print(f"   📊 API base: {data.get('api_base', 'N/A')}")
                        print(f"   📁 Upload folder: {data.get('upload_folder', 'N/A')}")
                    except:
                        pass

                elif endpoint == "/test/files":
                    try:
                        data = response.json()
                        test_count = data.get('total_test_images', 0)
                        upload_count = data.get('total_uploaded_files', 0)
                        print(f"   📊 Images de test: {test_count}, Fichiers uploadés: {upload_count}")
                    except:
                        pass

                results.append((endpoint, True, response.status_code))
            else:
                print(f"   ❌ {response.status_code} - Erreur")
                results.append((endpoint, False, response.status_code))

        except requests.exceptions.ConnectionError:
            print(f"   ❌ Connexion refusée - Serveur non accessible")
            results.append((endpoint, False, "Connection Error"))
        except requests.exceptions.Timeout:
            print(f"   ❌ Timeout - Serveur trop lent")
            results.append((endpoint, False, "Timeout"))
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            results.append((endpoint, False, str(e)))

    # Résumé
    print("\n" + "=" * 55)
    print("📋 Résumé des tests:")

    success_count = sum(1 for _, success, _ in results if success)
    total_count = len(results)

    for endpoint, success, status in results:
        status_icon = "✅" if success else "❌"
        print(f"   {status_icon} {endpoint} - {status}")

    print(f"\n🎯 Résultat: {success_count}/{total_count} tests réussis")

    if success_count == total_count:
        print("✅ Tous les tests sont passés ! L'interface est opérationnelle.")
        print(f"🌐 Ouvrez votre navigateur sur: {base_url}/test")
    else:
        print("❌ Certains tests ont échoué.")
        print("💡 Vérifiez que l'application Flask est démarrée avec:")
        print("   python run.py")
        print("   ou")
        print("   python scripts/run_test_interface.py")

    return success_count == total_count

def main():
    """Fonction principale."""
    import argparse

    parser = argparse.ArgumentParser(description="Test de l'interface web JPEG Stéganographie")
    parser.add_argument("--url", default="http://localhost:5000",
                       help="URL de base du serveur (défaut: http://localhost:5000)")

    args = parser.parse_args()

    success = test_interface_endpoints(args.url)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
