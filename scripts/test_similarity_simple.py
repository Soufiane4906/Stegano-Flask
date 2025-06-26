#!/usr/bin/env python3
"""
Test simple et direct de la similarité.
"""

import requests
import os

def test_similarity_simple():
    """Test super simple de l'endpoint de similarité."""

    # Prendre deux images du dossier uploads
    uploads_dir = "uploads"
    images = [f for f in os.listdir(uploads_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]

    if len(images) < 2:
        print("❌ Pas assez d'images dans uploads/")
        return False

    img1_path = os.path.join(uploads_dir, images[0])
    img2_path = os.path.join(uploads_dir, images[1])

    print(f"🖼️ Test avec: {images[0]} vs {images[1]}")

    try:
        # Faire la requête
        files = {
            'file1': ('img1.png', open(img1_path, 'rb'), 'image/png'),
            'file2': ('img2.png', open(img2_path, 'rb'), 'image/png')
        }

        response = requests.post("http://127.0.0.1:5000/api/images/similarity", files=files)

        print(f"📊 Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Succès!")

            if 'similarity' in result:
                sim = result['similarity']
                print(f"📈 Similarité moyenne: {sim.get('average', 'N/A')}%")
                print(f"📈 pHash: {sim.get('phash', 'N/A')}%")
                print(f"📈 dHash: {sim.get('dhash', 'N/A')}%")
                return True
            else:
                print(f"❌ Format incorrect: {result}")
                return False
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Test simple de similarité")
    print("=" * 40)
    success = test_similarity_simple()
    print(f"\n📊 Résultat: {'✅ PASS' if success else '❌ FAIL'}")
