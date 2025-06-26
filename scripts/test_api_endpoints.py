#!/usr/bin/env python3
"""
Test des endpoints de stéganographie via l'API REST.
"""

import requests
import os
from PIL import Image
import io

def test_steganography_endpoints():
    """Test complet des endpoints de stéganographie."""
    base_url = "http://127.0.0.1:5000"

    print("🌐 Test des endpoints de stéganographie")
    print("=" * 50)

    # Créer une image de test
    test_image = Image.new('RGB', (200, 200), color='red')
    img_bytes = io.BytesIO()
    test_image.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    try:
        # Test 1: Cacher un message
        print("📝 Test 1: Endpoint /api/images/hide")
        files = {'file': ('test.png', img_bytes, 'image/png')}
        data = {'message': 'Message secret de test'}

        response = requests.post(f"{base_url}/api/images/hide", files=files, data=data)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Succès: {result}")

            if 'data' in result and 'image_url' in result['data']:
                image_url = result['data']['image_url']
                print(f"🖼️ Image créée: {image_url}")

                # Test 2: Télécharger l'image créée et révéler le message
                print(f"\n🔍 Test 2: Endpoint /api/images/reveal")

                # Télécharger l'image
                img_response = requests.get(f"{base_url}{image_url}")
                if img_response.status_code == 200:
                    # Envoyer l'image pour révélation
                    files = {'file': ('steg_test.png', io.BytesIO(img_response.content), 'image/png')}
                    reveal_response = requests.post(f"{base_url}/api/images/reveal", files=files)

                    print(f"Status: {reveal_response.status_code}")

                    if reveal_response.status_code == 200:
                        reveal_result = reveal_response.json()
                        print(f"✅ Résultat: {reveal_result}")

                        if 'message' in reveal_result and reveal_result['message']:
                            print(f"🎉 Message révélé: '{reveal_result['message']}'")
                            return True
                        else:
                            print("❌ Aucun message trouvé")
                            return False
                    else:
                        print(f"❌ Erreur révélation: {reveal_response.text}")
                        return False
                else:
                    print(f"❌ Impossible de télécharger l'image: {img_response.status_code}")
                    return False
            else:
                print(f"❌ Format de retour incorrect: {result}")
                return False
        else:
            print(f"❌ Erreur: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

def test_with_existing_image():
    """Test avec l'image problématique mentionnée."""
    print("\n🖼️ Test avec l'image spécifique")
    print("=" * 50)

    base_url = "http://127.0.0.1:5000"
    image_path = "uploads/8fffe33e-1b5a-49aa-9efa-cab162d7cdc2_steg.png"

    if not os.path.exists(image_path):
        print(f"❌ Image non trouvée: {image_path}")
        return False

    try:
        # Lire l'image
        with open(image_path, 'rb') as f:
            files = {'file': ('test_image.png', f, 'image/png')}
            response = requests.post(f"{base_url}/api/images/reveal", files=files)

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Résultat: {result}")

            if 'message' in result and result['message']:
                print(f"🎉 Message trouvé: '{result['message']}'")
                return True
            else:
                print("❌ Aucun message secret trouvé")
                return False
        else:
            print(f"❌ Erreur: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Test des endpoints de stéganographie")
    print("=" * 60)

    # Vérifier que le serveur est accessible
    try:
        response = requests.get("http://127.0.0.1:5000")
        if response.status_code != 200 and response.status_code != 404:
            print("❌ Serveur Flask non accessible sur http://127.0.0.1:5000")
            print("💡 Lancez d'abord le serveur avec: python run.py")
            exit(1)
    except:
        print("❌ Serveur Flask non accessible sur http://127.0.0.1:5000")
        print("💡 Lancez d'abord le serveur avec: python run.py")
        exit(1)

    # Test 1: Test complet avec création et révélation
    success1 = test_steganography_endpoints()

    # Test 2: Test avec l'image problématique
    success2 = test_with_existing_image()

    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ")
    print("=" * 60)
    print(f"Test création/révélation: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"Test image spécifique: {'✅ PASS' if success2 else '❌ FAIL'}")

    if success1:
        print("\n🎉 Les endpoints de stéganographie fonctionnent correctement!")
        print("💡 L'interface web devrait maintenant fonctionner.")
    else:
        print("\n⚠️ Problème avec les endpoints de stéganographie.")
        print("💡 Vérifiez les logs du serveur Flask.")
