#!/usr/bin/env python3
"""
Script de test pour valider les corrections apportées à l'interface.
"""

import sys
import os
from pathlib import Path

# Ajouter le dossier racine au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_jpeg_service():
    """Teste le service JPEG après les corrections."""
    
    print("🧪 Test du service JPEG après corrections")
    print("=" * 50)
    
    try:
        from app.services.jpeg_steganography_service import JPEGSteganographyService
        
        service = JPEGSteganographyService()
        print("✅ Service JPEG initialisé avec succès")
        
        # Test si piexif est disponible
        try:
            import piexif
            print("✅ Bibliothèque piexif disponible")
        except ImportError:
            print("❌ Bibliothèque piexif manquante")
            return False
        
        # Tester avec une image de test si elle existe
        test_images = ['test_images/test_image_1.jpg', 'test_uploads/test.jpg']
        test_image = None
        
        for img_path in test_images:
            if os.path.exists(img_path):
                test_image = img_path
                break
        
        if test_image:
            print(f"📁 Image de test trouvée: {test_image}")
            
            # Test de l'analyse de capacité
            print("\n🔍 Test de l'analyse de capacité...")
            try:
                result = service.analyze_jpeg_capacity(test_image)
                
                if 'error' not in result:
                    print("✅ Analyse de capacité réussie")
                    print(f"   📏 Dimensions: {result.get('image_info', {}).get('dimensions', 'N/A')}")
                    print(f"   📤 Capacité EXIF: {result.get('exif_capacity', 'N/A')} caractères")
                    print(f"   📤 Capacité LSB: {result.get('lsb_capacity', 'N/A')} caractères")
                else:
                    print(f"❌ Erreur d'analyse: {result['error']}")
                    return False
            except Exception as e:
                print(f"❌ Exception lors de l'analyse: {e}")
                return False
            
            # Test de dissimulation EXIF
            print("\n🔐 Test de dissimulation EXIF...")
            try:
                output_path = "uploads/test_hide_output.jpg"
                os.makedirs("uploads", exist_ok=True)
                
                result = service.hide_message_in_jpeg(
                    test_image, 
                    "Message de test après correction 🔧", 
                    output_path, 
                    method='exif'
                )
                
                if result.get('success', False):
                    print("✅ Dissimulation EXIF réussie")
                    print(f"   📄 Fichier créé: {output_path}")
                    
                    # Test d'extraction
                    print("\n🔍 Test d'extraction EXIF...")
                    extract_result = service.extract_message_from_jpeg(output_path, method='exif')
                    
                    if extract_result.get('success', False) and extract_result.get('message'):
                        print("✅ Extraction EXIF réussie")
                        print(f"   💬 Message récupéré: {extract_result['message']}")
                    else:
                        print(f"❌ Erreur d'extraction: {extract_result.get('error', 'Message non trouvé')}")
                        return False
                else:
                    print(f"❌ Erreur de dissimulation: {result.get('error', 'Erreur inconnue')}")
                    return False
                    
            except Exception as e:
                print(f"❌ Exception lors de la dissimulation: {e}")
                return False
        else:
            print("⚠️ Aucune image de test trouvée")
            print("💡 Placez une image JPEG dans test_images/test_image_1.jpg pour tester")
        
        print("\n🎉 Tous les tests de base sont passés !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        return False

def test_interface_structure():
    """Teste que les routes de l'interface sont bien configurées."""
    
    print("\n🌐 Test de la structure de l'interface")
    print("=" * 50)
    
    try:
        from app import create_app
        
        app = create_app()
        
        with app.test_client() as client:
            # Test de la route principale de l'interface
            print("🔍 Test de la route /test...")
            response = client.get('/test')
            
            if response.status_code == 200:
                print("✅ Route /test accessible")
            else:
                print(f"❌ Route /test inaccessible (code: {response.status_code})")
                return False
            
            # Test de la route de statut
            print("🔍 Test de la route /test/status...")
            response = client.get('/test/status')
            
            if response.status_code == 200:
                print("✅ Route /test/status accessible")
                data = response.get_json()
                print(f"   📊 API base: {data.get('api_base', 'N/A')}")
            else:
                print(f"❌ Route /test/status inaccessible (code: {response.status_code})")
                return False
            
            # Test de la route des méthodes JPEG
            print("🔍 Test de la route /api/v2/jpeg/methods...")
            response = client.get('/api/v2/jpeg/methods')
            
            if response.status_code == 200:
                print("✅ API JPEG accessible")
                data = response.get_json()
                methods = list(data.get('methods', {}).keys())
                print(f"   🔧 Méthodes disponibles: {', '.join(methods)}")
            else:
                print(f"❌ API JPEG inaccessible (code: {response.status_code})")
                return False
        
        print("✅ Structure de l'interface validée")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test de l'interface: {e}")
        return False

def main():
    """Fonction principale."""
    
    print("🔧 Validation des corrections - Interface JPEG Stéganographie")
    print("=" * 70)
    
    success_count = 0
    total_tests = 2
    
    # Test 1: Service JPEG
    if test_jpeg_service():
        success_count += 1
    
    # Test 2: Structure de l'interface
    if test_interface_structure():
        success_count += 1
    
    # Résumé
    print("\n" + "=" * 70)
    print(f"📋 Résumé: {success_count}/{total_tests} tests réussis")
    
    if success_count == total_tests:
        print("🎉 Toutes les corrections ont été validées !")
        print("\n💡 Pour utiliser l'interface:")
        print("   1. Lancez: python run.py")
        print("   2. Ouvrez: http://localhost:5000/test")
        print("   3. Testez avec des images JPEG")
        
        return True
    else:
        print("❌ Certaines corrections nécessitent encore du travail")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
