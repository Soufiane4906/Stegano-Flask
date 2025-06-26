#!/usr/bin/env python3
"""
Test final après corrections des services
"""

import requests
import os
import time

def test_updated_services():
    """Test les services mis à jour"""
    base_url = "http://localhost:5000"

    # Trouver une image de test
    test_image = None
    for ext in ['png', 'jpg', 'jpeg']:
        for file in os.listdir('test_images'):
            if file.lower().endswith(ext):
                test_image = os.path.join('test_images', file)
                break
        if test_image:
            break

    if not test_image:
        print("❌ Aucune image de test trouvée")
        return

    print(f"📸 Utilisation de l'image: {test_image}")

    tests = [
        {
            "name": "🤖 Détection IA",
            "url": f"{base_url}/api/images/ai-detection",
            "files": {"file": open(test_image, 'rb')},
            "expected": ["is_ai_generated", "confidence"]
        },
        {
            "name": "🔍 Stéganographie Hide",
            "url": f"{base_url}/api/images/hide",
            "files": {"file": open(test_image, 'rb')},
            "data": {"message": "Test secret message"},
            "expected": ["success", "data"]
        },
        {
            "name": "🔎 Stéganographie Reveal",
            "url": f"{base_url}/api/images/reveal",
            "files": {"file": open(test_image, 'rb')},
            "expected": ["success"]
        }
    ]

    print("\n" + "="*60)
    print("🧪 TEST DES SERVICES CORRIGÉS")
    print("="*60)

    for test in tests:
        print(f"\n🔍 Test: {test['name']}")

        try:
            # Préparer les fichiers
            files = test['files']
            data = test.get('data', {})

            # Envoyer la requête
            response = requests.post(test['url'], files=files, data=data, timeout=30)

            if response.status_code == 200:
                result = response.json()
                print(f"✅ Status: 200 OK")

                # Vérifier les champs attendus
                all_present = all(key in result for key in test['expected'])
                if all_present:
                    print(f"✅ Champs attendus présents: {test['expected']}")
                    print(f"📄 Réponse: {str(result)[:100]}...")
                else:
                    print(f"⚠️ Champs manquants dans la réponse")
                    print(f"📄 Réponse complète: {result}")

            else:
                print(f"❌ Status: {response.status_code}")
                try:
                    error = response.json()
                    print(f"📄 Erreur: {error}")
                except:
                    print(f"📄 Erreur: {response.text}")

        except requests.exceptions.ConnectionError:
            print(f"❌ Connexion refusée - Vérifiez que l'app tourne")
        except Exception as e:
            print(f"❌ Erreur: {str(e)}")
        finally:
            # Fermer les fichiers
            for f in test['files'].values():
                if hasattr(f, 'close'):
                    f.close()

    # Test de similarité avec deux fichiers
    print(f"\n🔍 Test: 📊 Similarité d'images")
    try:
        with open(test_image, 'rb') as f1, open(test_image, 'rb') as f2:
            files = {'file1': f1, 'file2': f2}
            response = requests.post(f"{base_url}/api/images/similarity", files=files, timeout=30)

            if response.status_code == 200:
                result = response.json()
                print(f"✅ Status: 200 OK")
                if 'similarity' in result:
                    print(f"✅ Similarité calculée: {result['similarity']}")
                else:
                    print(f"⚠️ Champ 'similarity' manquant")
                    print(f"📄 Réponse: {result}")
            else:
                print(f"❌ Status: {response.status_code}")
                print(f"📄 Erreur: {response.text}")

    except Exception as e:
        print(f"❌ Erreur: {str(e)}")

    print("\n" + "="*60)
    print("✨ Tests terminés !")
    print("="*60)

if __name__ == "__main__":
    print("🚀 Test des services corrigés")
    print("💡 Assurez-vous que l'application tourne (python run.py)")
    print()

    # Attendre que l'utilisateur démarre l'app
    time.sleep(2)

    test_updated_services()
