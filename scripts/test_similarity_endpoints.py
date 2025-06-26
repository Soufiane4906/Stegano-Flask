#!/usr/bin/env python3
"""
Test de l'endpoint de similarité d'images.
"""

import requests
import os
from PIL import Image
import io

def create_test_images():
    """Crée des images de test pour la comparaison."""
    print("🎨 Création d'images de test...")

    # Image 1 - Rouge
    img1 = Image.new('RGB', (200, 200), color='red')
    img1_bytes = io.BytesIO()
    img1.save(img1_bytes, format='PNG')
    img1_bytes.seek(0)

    # Image 2 - Rouge similaire (même couleur)
    img2 = Image.new('RGB', (200, 200), color='red')
    img2_bytes = io.BytesIO()
    img2.save(img2_bytes, format='PNG')
    img2_bytes.seek(0)

    # Image 3 - Bleue (différente)
    img3 = Image.new('RGB', (200, 200), color='blue')
    img3_bytes = io.BytesIO()
    img3.save(img3_bytes, format='PNG')
    img3_bytes.seek(0)

    return img1_bytes, img2_bytes, img3_bytes

def test_similarity_endpoint():
    """Test de l'endpoint de similarité."""
    base_url = "http://127.0.0.1:5000"

    print("🔍 Test de l'endpoint de similarité")
    print("=" * 50)

    try:
        # Créer les images de test
        img1_bytes, img2_bytes, img3_bytes = create_test_images()

        # Test 1: Images similaires (rouge vs rouge)
        print("\n📊 Test 1: Images similaires (rouge vs rouge)")
        files = {
            'file1': ('test1.png', img1_bytes, 'image/png'),
            'file2': ('test2.png', img2_bytes, 'image/png')
        }

        response = requests.post(f"{base_url}/api/images/similarity", files=files)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Résultat: {result}")

            # Vérifier le format attendu par l'interface web
            if 'similarity_score' in result and 'details' in result:
                similarity_percent = result['similarity_score'] * 100
                print(f"🎯 Score de similarité: {similarity_percent:.1f}%")
                print(f"📊 Détails: {result['details']}")

                # Les images identiques devraient avoir une similarité élevée
                if similarity_percent > 90:
                    print("✅ Test images similaires: PASS")
                    test1_success = True
                else:
                    print(f"❌ Test images similaires: FAIL (similarité trop faible: {similarity_percent:.1f}%)")
                    test1_success = False
            else:
                print(f"❌ Format de retour incorrect: {result}")
                test1_success = False
        else:
            print(f"❌ Erreur: {response.text}")
            test1_success = False

        # Reset des BytesIO pour le test suivant
        img1_bytes.seek(0)
        img3_bytes.seek(0)

        # Test 2: Images différentes (rouge vs bleu)
        print("\n📊 Test 2: Images différentes (rouge vs bleu)")
        files = {
            'file1': ('test1.png', img1_bytes, 'image/png'),
            'file2': ('test3.png', img3_bytes, 'image/png')
        }

        response = requests.post(f"{base_url}/api/images/similarity", files=files)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            similarity_percent = result.get('similarity_score', 0) * 100
            print(f"🎯 Score de similarité: {similarity_percent:.1f}%")

            # Les images différentes devraient avoir une similarité faible
            if similarity_percent < 50:
                print("✅ Test images différentes: PASS")
                test2_success = True
            else:
                print(f"❌ Test images différentes: FAIL (similarité trop élevée: {similarity_percent:.1f}%)")
                test2_success = False
        else:
            print(f"❌ Erreur: {response.text}")
            test2_success = False

        return test1_success and test2_success

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_similarity_validation():
    """Test de validation des paramètres."""
    base_url = "http://127.0.0.1:5000"

    print("\n🔒 Test de validation des paramètres")
    print("=" * 50)

    try:
        # Test avec un seul fichier (devrait échouer)
        img1_bytes, _, _ = create_test_images()

        files = {'file1': ('test1.png', img1_bytes, 'image/png')}
        response = requests.post(f"{base_url}/api/images/similarity", files=files)

        print(f"Status: {response.status_code}")

        if response.status_code == 400:
            result = response.json()
            print(f"✅ Validation OK: {result.get('error', '')}")
            return True
        else:
            print(f"❌ Validation échouée: devrait retourner 400")
            return False

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_interface_web():
    """Test de l'interface web de similarité."""
    print("\n🌐 Test de l'interface web")
    print("=" * 50)

    try:
        response = requests.get("http://127.0.0.1:5000/similarity.html")

        if response.status_code == 200:
            print("✅ Interface similarity.html accessible")

            # Vérifier que l'interface contient les éléments nécessaires
            content = response.text
            if "/api/images/similarity" in content:
                print("✅ Interface utilise le bon endpoint")
                return True
            else:
                print("❌ Interface n'utilise pas le bon endpoint")
                return False
        else:
            print(f"❌ Interface non accessible: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Test complet de la similarité d'images")
    print("=" * 60)

    # Vérifier que le serveur est accessible
    try:
        response = requests.get("http://127.0.0.1:5000")
        if response.status_code not in [200, 404]:
            print("❌ Serveur Flask non accessible sur http://127.0.0.1:5000")
            print("💡 Lance le serveur avec: python run.py")
            exit(1)
    except:
        print("❌ Serveur Flask non accessible sur http://127.0.0.1:5000")
        print("💡 Lance le serveur avec: python run.py")
        exit(1)

    # Tests
    test_results = []

    # Test 1: Endpoint de similarité
    test_results.append(("Endpoint similarité", test_similarity_endpoint()))

    # Test 2: Validation des paramètres
    test_results.append(("Validation paramètres", test_similarity_validation()))

    # Test 3: Interface web
    test_results.append(("Interface web", test_interface_web()))

    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 60)

    passed = 0
    total = len(test_results)

    for test_name, success in test_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if success:
            passed += 1

    print(f"\n📈 Résultat: {passed}/{total} tests réussis")

    if passed == total:
        print("🎉 Tous les tests sont passés! L'interface de similarité fonctionne correctement.")
        print("🌐 Testez maintenant sur: http://127.0.0.1:5000/similarity.html")
    else:
        print("⚠️ Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")
