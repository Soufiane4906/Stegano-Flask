#!/usr/bin/env python3
"""
Script de validation post-organisation.
Vérifie que tous les composants fonctionnent encore après le nettoyage.
"""

import os
import sys
import importlib.util

def test_project_structure():
    """Vérifie que la structure du projet est correcte."""
    print("🏗️ Vérification de la structure du projet...")

    required_folders = [
        'app', 'docs', 'scripts', 'models', 'notebooks',
        'deployment', 'legacy', 'uploads', 'instance'
    ]

    missing_folders = []
    for folder in required_folders:
        if not os.path.exists(folder):
            missing_folders.append(folder)

    if missing_folders:
        print(f"❌ Dossiers manquants: {missing_folders}")
        return False
    else:
        print(f"✅ Tous les dossiers requis sont présents")
        return True

def test_app_imports():
    """Teste que l'application peut être importée."""
    print("\n📦 Test d'importation de l'application...")

    try:
        # Test d'import de l'app principale
        sys.path.insert(0, '.')
        from app import create_app
        app = create_app()
        print("✅ Application Flask importée avec succès")

        # Test des services
        from app.services.image_service import ImageService
        from app.services.steganography_service import SteganographyService
        from app.services.ai_detection_service_v2 import AIDetectionService
        print("✅ Services importés avec succès")

        return True

    except Exception as e:
        print(f"❌ Erreur d'importation: {e}")
        return False

def test_models_access():
    """Vérifie l'accès aux modèles IA."""
    print("\n🧠 Vérification des modèles IA...")

    model_files = ['model.h5', 'model_mobilenet.h5', 'model_simple.h5']
    found_models = []

    for model in model_files:
        model_path = os.path.join('models', model)
        if os.path.exists(model_path):
            found_models.append(model)
            print(f"✅ {model} trouvé")
        else:
            print(f"⚠️ {model} manquant")

    if found_models:
        print(f"✅ {len(found_models)}/{len(model_files)} modèles disponibles")
        return True
    else:
        print("❌ Aucun modèle disponible")
        return False

def test_scripts_availability():
    """Vérifie que les scripts sont accessibles."""
    print("\n🔧 Vérification des scripts...")

    important_scripts = [
        'scripts/test_final_complete.py',
        'scripts/init_db.py',
        'scripts/create_ai_model.py'
    ]

    available_scripts = []
    for script in important_scripts:
        if os.path.exists(script):
            available_scripts.append(script)
            print(f"✅ {script} disponible")
        else:
            print(f"❌ {script} manquant")

    return len(available_scripts) == len(important_scripts)

def test_documentation():
    """Vérifie que la documentation est complète."""
    print("\n📚 Vérification de la documentation...")

    doc_files = [
        'docs/RAPPORT_ACADEMIQUE.md',
        'docs/REFACTORING_SUCCESS_FINAL.md',
        'PROJECT_STRUCTURE.md',
        'ORGANISATION_RAPPORT.md'
    ]

    available_docs = []
    for doc in doc_files:
        if os.path.exists(doc):
            available_docs.append(doc)
            print(f"✅ {doc} disponible")
        else:
            print(f"❌ {doc} manquant")

    return len(available_docs) >= 3

def test_deployment_files():
    """Vérifie les fichiers de déploiement."""
    print("\n🐳 Vérification des fichiers de déploiement...")

    deploy_files = [
        'deployment/Dockerfile',
        'deployment/docker-compose.yml',
        '.github/workflows/ci-cd.yml'
    ]

    available_deploy = []
    for file in deploy_files:
        if os.path.exists(file):
            available_deploy.append(file)
            print(f"✅ {file} disponible")
        else:
            print(f"❌ {file} manquant")

    return len(available_deploy) >= 2

def test_basic_functionality():
    """Test basique de fonctionnalité."""
    print("\n⚡ Test de fonctionnalité basique...")

    try:
        # Test de création d'app
        from app import create_app
        app = create_app()

        with app.app_context():
            # Test des services
            from app.services.steganography_service import SteganographyService
            steg_service = SteganographyService()
            print("✅ Service de stéganographie initialisé")

            from app.services.ai_detection_service_v2 import AIDetectionService
            ai_service = AIDetectionService()
            print("✅ Service de détection IA initialisé")

            return True

    except Exception as e:
        print(f"❌ Erreur de fonctionnalité: {e}")
        return False

def generate_health_report():
    """Génère un rapport de santé du projet."""
    print("\n📊 GÉNÉRATION DU RAPPORT DE SANTÉ")
    print("=" * 50)

    tests = [
        ("Structure du projet", test_project_structure),
        ("Importations app", test_app_imports),
        ("Modèles IA", test_models_access),
        ("Scripts", test_scripts_availability),
        ("Documentation", test_documentation),
        ("Déploiement", test_deployment_files),
        ("Fonctionnalité", test_basic_functionality)
    ]

    results = []
    total_score = 0

    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
            if success:
                total_score += 1
        except Exception as e:
            print(f"❌ Erreur dans {test_name}: {e}")
            results.append((test_name, False))

    # Résumé
    print("\n" + "=" * 50)
    print("📋 RAPPORT DE SANTÉ POST-ORGANISATION")
    print("=" * 50)

    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")

    percentage = (total_score / len(tests)) * 100
    print(f"\n📈 Score global: {total_score}/{len(tests)} ({percentage:.1f}%)")

    if percentage >= 90:
        print("🎉 EXCELLENT! Projet parfaitement organisé.")
    elif percentage >= 75:
        print("✅ BON! Organisation réussie avec quelques points d'attention.")
    elif percentage >= 50:
        print("⚠️ MOYEN! Quelques problèmes à résoudre.")
    else:
        print("❌ CRITIQUE! Organisation à revoir.")

    return percentage >= 75

def main():
    """Fonction principale de validation."""
    print("🔍 VALIDATION POST-ORGANISATION")
    print("=" * 60)
    print("Vérification que le projet fonctionne après nettoyage...")

    success = generate_health_report()

    if success:
        print(f"\n✅ VALIDATION RÉUSSIE!")
        print(f"🎯 Le projet est prêt pour utilisation.")
        print(f"📖 Consultez PROJECT_STRUCTURE.md pour la navigation.")
    else:
        print(f"\n❌ VALIDATION ÉCHOUÉE!")
        print(f"🔧 Certains composants nécessitent une attention.")

    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
