#!/usr/bin/env python3
"""
Test rapide de l'endpoint de similarité.
"""

import requests
import os
import json

def quick_similarity_test():
    """Test rapide avec deux images du dossier uploads."""
    base_url = "http://127.0.0.1:5000"
    uploads_dir = "uploads"

    print("🚀 Test rapide de similarité")
    print("=" * 40)

    # Prendre les deux premières images PNG
    png_files = [f for f in os.listdir(uploads_dir) if f.endswith('.png')][:2]

    if len(png_files) < 2:
        print("❌ Pas assez d'images PNG dans uploads/")
        return False

    print(f"📸 Image 1: {png_files[0]}")
    print(f"📸 Image 2: {png_files[1]}")

    try:
        image1_path = os.path.join(uploads_dir, png_files[0])
        image2_path = os.path.join(uploads_dir, png_files[1])

        with open(image1_path, 'rb') as f1, open(image2_path, 'rb') as f2:
            files = {
                'file1': (png_files[0], f1, 'image/png'),
                'file2': (png_files[1], f2, 'image/png')
            }

            print("📡 Envoi de la requête...")
            response = requests.post(f"{base_url}/api/images/similarity", files=files, timeout=15)

        print(f"📊 Status Code: {response.status_code}")

        if response.status_code == 200:
            try:
                result = response.json()
                print("✅ Réponse JSON reçue:")
                print(json.dumps(result, indent=2))

                if 'similarity_score' in result:
                    print(f"\n🎯 Score de similarité: {result['similarity_score']}%")
                    print("✅ Format correct pour l'interface web!")
                    return True
                else:
                    print("❌ Champ 'similarity_score' manquant")
                    return False

            except json.JSONDecodeError as e:
                print(f"❌ Erreur de décodage JSON: {e}")
                print(f"Réponse brute: {response.text}")
                return False

        else:
            print(f"❌ Erreur HTTP {response.status_code}")
            print(f"Réponse: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

if __name__ == "__main__":
    success = quick_similarity_test()

    if success:
        print("\n🎉 Test réussi! L'interface web devrait fonctionner.")
        print("🌐 Testez sur: http://127.0.0.1:5000/similarity.html")
    else:
        print("\n⚠️ Test échoué. Vérifiez les logs du serveur Flask.")
        print("💡 Le serveur Flask est-il démarré sur le port 5000?")
