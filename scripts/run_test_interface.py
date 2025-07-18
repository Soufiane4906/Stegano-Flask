#!/usr/bin/env python3
"""
Script pour lancer l'interface de test web de la stéganographie JPEG.

Ce script démarre l'application Flask et ouvre automatiquement l'interface
de test dans le navigateur par défaut.

Usage:
    python scripts/run_test_interface.py
"""

import os
import sys
import time
import threading
import webbrowser
from pathlib import Path

# Ajouter le dossier racine au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

def print_colored(message, color='white'):
    """Affiche un message coloré dans le terminal."""
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'reset': '\033[0m'
    }

    color_code = colors.get(color.lower(), colors['white'])
    reset_code = colors['reset']
    print(f"{color_code}{message}{reset_code}")

def check_dependencies():
    """Vérifie que les dépendances sont installées."""
    try:
        from app import create_app
        from flask import Flask
        return True
    except ImportError as e:
        print_colored(f"❌ Dépendance manquante: {e}", 'red')
        print_colored("💡 Installez les dépendances avec: pip install -r requirements.txt", 'yellow')
        return False

def create_test_directories():
    """Crée les dossiers nécessaires pour les tests."""
    directories = ['uploads', 'test_images', 'logs']

    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print_colored(f"📁 Dossier créé: {directory}/", 'green')

def create_sample_test_image():
    """Crée une image de test simple si aucune n'existe."""
    test_images_dir = 'test_images'
    sample_image = os.path.join(test_images_dir, 'sample_test.jpg')

    if not os.path.exists(sample_image):
        try:
            from PIL import Image
            import numpy as np

            # Créer une image simple RGB
            img_array = np.random.randint(0, 256, (300, 400, 3), dtype=np.uint8)
            img = Image.fromarray(img_array, 'RGB')
            img.save(sample_image, 'JPEG', quality=95)
            print_colored(f"🖼️ Image de test créée: {sample_image}", 'green')
            return True
        except ImportError:
            print_colored("⚠️ PIL non disponible pour créer une image de test", 'yellow')
            return False
    return True

def open_browser_after_delay(url, delay=2):
    """Ouvre le navigateur après un délai."""
    time.sleep(delay)
    try:
        webbrowser.open(url)
        print_colored(f"🌐 Interface ouverte dans le navigateur: {url}", 'cyan')
    except Exception as e:
        print_colored(f"⚠️ Impossible d'ouvrir le navigateur automatiquement: {e}", 'yellow')
        print_colored(f"💡 Ouvrez manuellement: {url}", 'cyan')

def main():
    """Fonction principale."""
    print_colored("🚀 Interface de Test - JPEG Stéganographie", 'magenta')
    print_colored("=" * 50, 'magenta')

    # Vérifier les dépendances
    if not check_dependencies():
        sys.exit(1)

    # Créer les dossiers nécessaires
    create_test_directories()

    # Créer une image de test si nécessaire
    create_sample_test_image()

    try:
        # Importer et créer l'application
        from app import create_app
        app = create_app()

        # Configuration pour le développement
        app.config['DEBUG'] = True
        app.config['TESTING'] = True

        print_colored("\n📋 Configuration:", 'blue')
        print_colored(f"  🌐 URL principale: http://localhost:5000", 'white')
        print_colored(f"  🧪 Interface de test: http://localhost:5000/test", 'white')
        print_colored(f"  📊 API JPEG: http://localhost:5000/api/v2/jpeg", 'white')
        print_colored(f"  📁 Dossier uploads: uploads/", 'white')
        print_colored(f"  🖼️ Images de test: test_images/", 'white')

        print_colored("\n🎯 Instructions:", 'blue')
        print_colored("  1. L'interface de test va s'ouvrir automatiquement", 'white')
        print_colored("  2. Sélectionnez une image JPEG dans 'test_images/'", 'white')
        print_colored("  3. Testez les différentes fonctionnalités", 'white')
        print_colored("  4. Appuyez Ctrl+C pour arrêter le serveur", 'white')

        # Programmer l'ouverture du navigateur
        browser_thread = threading.Thread(
            target=open_browser_after_delay,
            args=("http://localhost:5000/test", 3)
        )
        browser_thread.daemon = True
        browser_thread.start()

        print_colored("\n🔥 Démarrage du serveur Flask...", 'green')
        print_colored("-" * 50, 'green')

        # Lancer l'application
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=False  # Éviter les problèmes avec le threading
        )

    except KeyboardInterrupt:
        print_colored("\n\n🛑 Serveur arrêté par l'utilisateur", 'yellow')
        print_colored("✅ Interface de test fermée", 'green')
    except Exception as e:
        print_colored(f"\n❌ Erreur lors du démarrage: {e}", 'red')
        print_colored("💡 Vérifiez que le port 5000 est libre", 'yellow')
        sys.exit(1)

if __name__ == "__main__":
    main()
