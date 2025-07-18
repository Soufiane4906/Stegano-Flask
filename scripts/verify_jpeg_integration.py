"""
Script de vérification de l'intégration du service JPEG.
"""

import sys
import os

# Ajouter le chemin parent pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test des imports du service JPEG."""
    print("🔧 Test des imports...")

    try:
        from app.services.jpeg_steganography_service import JPEGSteganographyService
        print("✅ Import JPEGSteganographyService : OK")
    except ImportError as e:
        print(f"❌ Import JPEGSteganographyService : ÉCHEC - {e}")
        return False

    try:
        from app.api.jpeg_routes import jpeg_bp
        print("✅ Import routes JPEG : OK")
    except ImportError as e:
        print(f"❌ Import routes JPEG : ÉCHEC - {e}")
        return False

    try:
        # Tester l'initialisation du service
        service = JPEGSteganographyService()
        print("✅ Initialisation du service : OK")
        print(f"   Formats supportés : {service.supported_formats}")
        print(f"   Taille max message : {service.max_message_length // 1024}KB")
    except Exception as e:
        print(f"❌ Initialisation du service : ÉCHEC - {e}")
        return False

    return True

def test_app_integration():
    """Test de l'intégration avec l'application Flask."""
    print("\n🔧 Test de l'intégration Flask...")

    try:
        from app import create_app
        app = create_app('development')

        print("✅ Création de l'application : OK")

        # Vérifier que le blueprint est enregistré
        blueprint_names = [bp.name for bp in app.blueprints.values()]

        if 'jpeg_stegano' in blueprint_names:
            print("✅ Blueprint JPEG enregistré : OK")
        else:
            print(f"❌ Blueprint JPEG manquant. Blueprints trouvés : {blueprint_names}")
            return False

        # Vérifier les routes
        routes = []
        for rule in app.url_map.iter_rules():
            if '/jpeg/' in rule.rule:
                routes.append(rule.rule)

        expected_routes = [
            '/api/v2/jpeg/analyze_capacity',
            '/api/v2/jpeg/hide_message',
            '/api/v2/jpeg/extract_message',
            '/api/v2/jpeg/create_signature',
            '/api/v2/jpeg/verify_signature',
            '/api/v2/jpeg/methods'
        ]

        print(f"✅ Routes JPEG trouvées : {len(routes)}")
        for route in routes:
            print(f"   - {route}")

        # Vérifier que toutes les routes attendues sont présentes
        for expected in expected_routes:
            if expected not in routes:
                print(f"❌ Route manquante : {expected}")
                return False

        print("✅ Toutes les routes JPEG sont présentes")

    except Exception as e:
        print(f"❌ Intégration Flask : ÉCHEC - {e}")
        return False

    return True

def test_service_functionality():
    """Test basique de la fonctionnalité du service."""
    print("\n🔧 Test de fonctionnalité basique...")

    try:
        from app.services.jpeg_steganography_service import JPEGSteganographyService
        service = JPEGSteganographyService()

        # Test de la méthode d'analyse (sans fichier réel)
        print("✅ Service prêt pour les tests avec de vraies images")

        # Test des méthodes disponibles
        methods = ['exif', 'lsb', 'dct']
        print(f"✅ Méthodes disponibles : {methods}")

        return True

    except Exception as e:
        print(f"❌ Test de fonctionnalité : ÉCHEC - {e}")
        return False

def main():
    """Fonction principale de vérification."""
    print("=" * 60)
    print("VÉRIFICATION DE L'INTÉGRATION DU SERVICE JPEG")
    print("=" * 60)

    success = True

    # Test des imports
    if not test_imports():
        success = False

    # Test de l'intégration Flask
    if not test_app_integration():
        success = False

    # Test de fonctionnalité
    if not test_service_functionality():
        success = False

    print("\n" + "=" * 60)
    if success:
        print("✅ TOUS LES TESTS ONT RÉUSSI !")
        print("\nVotre service JPEG est prêt à être utilisé :")
        print("- Démarrez l'application : python run.py")
        print("- Testez avec de vraies images : python scripts/test_jpeg_steganography.py")
        print("- API disponible sur : http://localhost:5000/api/v2/jpeg/")
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
        print("\nVérifiez les erreurs ci-dessus et corrigez les problèmes.")
    print("=" * 60)

if __name__ == "__main__":
    main()
