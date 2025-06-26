#!/usr/bin/env python3
"""
Test et diagnostic de la comparaison de similarité d'images.
"""

import os
import sys
import requests
import json

# Ajouter le répertoire du projet au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_similarity_service():
    """Test direct du service de similarité."""
    print("🔍 Test du service de similarité")
    print("=" * 50)

    try:
        from app.services.image_service import ImageService
        from app.services.ai_detection_service_v2 import AIDetectionService
        from werkzeug.datastructures import FileStorage
        import io
        from PIL import Image

        # Initialiser les services
        ai_service = AIDetectionService()
        image_service = ImageService("uploads", ai_service)

        # Créer deux images de test similaires
        print("📸 Création d'images de test...")
        img1 = Image.new('RGB', (100, 100), color='blue')
        img2 = Image.new('RGB', (100, 100), color='blue')  # Identique

        # Convertir en FileStorage
        img1_bytes = io.BytesIO()
        img1.save(img1_bytes, format='PNG')
        img1_bytes.seek(0)
        file1 = FileStorage(img1_bytes, filename='test1.png', content_type='image/png')

        img2_bytes = io.BytesIO()
        img2.save(img2_bytes, format='PNG')
        img2_bytes.seek(0)
        file2 = FileStorage(img2_bytes, filename='test2.png', content_type='image/png')

        # Tester la comparaison
        print("🔍 Test de comparaison...")
        result = image_service.compare_similarity(file1, file2)
        print(f"✅ Résultat: {json.dumps(result, indent=2)}")

        if 'similarity' in result and 'average' in result['similarity']:
            similarity_score = result['similarity']['average']
            print(f"📊 Score de similarité: {similarity_score}%")
            return True
        else:
            print(f"❌ Format de retour incorrect: {result}")
            return False

    except Exception as e:
        print(f"❌ Erreur dans le service: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_similarity_endpoint():
    """Test de l'endpoint REST de similarité."""
    print("\n🌐 Test de l'endpoint /api/images/similarity")
    print("=" * 50)

    base_url = "http://127.0.0.1:5000"

    try:
        # Vérifier que le serveur est accessible
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"🌐 Serveur accessible: {response.status_code}")
    except:
        print("❌ Serveur non accessible sur http://127.0.0.1:5000")
        return False

    try:
        # Utiliser deux images existantes du dossier uploads
        uploads_dir = "uploads"
        image_files = [f for f in os.listdir(uploads_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]

        if len(image_files) < 2:
            print("❌ Pas assez d'images dans le dossier uploads")
            return False

        image1_path = os.path.join(uploads_dir, image_files[0])
        image2_path = os.path.join(uploads_dir, image_files[1])

        print(f"📸 Image 1: {image_files[0]}")
        print(f"📸 Image 2: {image_files[1]}")

        # Préparer les fichiers pour l'upload
        with open(image1_path, 'rb') as f1, open(image2_path, 'rb') as f2:
            files = {
                'file1': (image_files[0], f1, 'image/png'),
                'file2': (image_files[1], f2, 'image/png')
            }

            # Appeler l'endpoint
            response = requests.post(f"{base_url}/api/images/similarity", files=files, timeout=30)

        print(f"📡 Status: {response.status_code}")
        print(f"📡 Headers: {dict(response.headers)}")

        if response.status_code == 200:
            try:
                result = response.json()
                print(f"✅ Réponse JSON: {json.dumps(result, indent=2)}")

                # Vérifier le format attendu par l'interface
                if 'similarity_score' in result:
                    print(f"🎯 Score principal: {result['similarity_score']}%")
                    return True
                elif 'similarity' in result and 'average' in result['similarity']:
                    print(f"🎯 Score trouvé dans similarity.average: {result['similarity']['average']}%")
                    print("⚠️ Format non compatible avec l'interface HTML")
                    return False
                else:
                    print("❌ Format de retour non reconnu")
                    return False

            except json.JSONDecodeError:
                print(f"❌ Réponse non-JSON: {response.text}")
                return False
        else:
            print(f"❌ Erreur HTTP: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Erreur lors du test d'endpoint: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_with_specific_images():
    """Test avec des images spécifiques du dossier uploads."""
    print("\n🖼️ Test avec images spécifiques")
    print("=" * 50)

    base_url = "http://127.0.0.1:5000"
    uploads_dir = "uploads"

    # Chercher des images avec et sans stéganographie pour tester la similarité
    steg_pairs = []
    image_files = os.listdir(uploads_dir)

    for filename in image_files:
        if filename.endswith('_steg.png'):
            original = filename.replace('_steg.png', '.png')
            if original in image_files:
                steg_pairs.append((original, filename))

    if not steg_pairs:
        print("❌ Aucune paire d'images original/stéganographie trouvée")
        return False

    print(f"📸 Paires trouvées: {len(steg_pairs)}")

    for original, steg in steg_pairs[:2]:  # Tester seulement les 2 premières paires
        print(f"\n🔍 Test: {original} vs {steg}")

        try:
            image1_path = os.path.join(uploads_dir, original)
            image2_path = os.path.join(uploads_dir, steg)

            with open(image1_path, 'rb') as f1, open(image2_path, 'rb') as f2:
                files = {
                    'file1': (original, f1, 'image/png'),
                    'file2': (steg, f2, 'image/png')
                }

                response = requests.post(f"{base_url}/api/images/similarity", files=files, timeout=30)

            if response.status_code == 200:
                result = response.json()
                if 'similarity_score' in result:
                    score = result['similarity_score']
                    print(f"✅ Similarité: {score}% (attendu: élevé car même image de base)")
                elif 'similarity' in result:
                    score = result['similarity'].get('average', 'N/A')
                    print(f"⚠️ Similarité (format ancien): {score}%")
                else:
                    print(f"❌ Format inattendu: {result}")
            else:
                print(f"❌ Erreur: {response.status_code} - {response.text}")

        except Exception as e:
            print(f"❌ Erreur pour {original} vs {steg}: {e}")

    return True

if __name__ == "__main__":
    print("🧪 DIAGNOSTIC COMPLET - SIMILARITÉ D'IMAGES")
    print("=" * 60)

    # Test 1: Service direct
    success1 = test_similarity_service()

    # Test 2: Endpoint REST
    success2 = test_similarity_endpoint()

    # Test 3: Images spécifiques
    success3 = test_with_specific_images()

    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 60)
    print(f"Service direct: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"Endpoint REST: {'✅ PASS' if success2 else '❌ FAIL'}")
    print(f"Images spécifiques: {'✅ PASS' if success3 else '❌ FAIL'}")

    if success1 and not success2:
        print("\n💡 DIAGNOSTIC:")
        print("- Le service fonctionne correctement")
        print("- L'endpoint a un problème de format de retour")
        print("- Correction nécessaire dans l'API")
    elif not success1:
        print("\n💡 DIAGNOSTIC:")
        print("- Problème dans le service de base")
        print("- Vérifiez les dépendances (imagehash, scipy)")
    else:
        print("\n🎉 Tous les tests sont OK!")

    print(f"\n🌐 Interface web: http://127.0.0.1:5000/similarity.html")
