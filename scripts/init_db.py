#!/usr/bin/env python3
"""
Script pour initialiser la base de données.
"""

import os
import sys

# Ajouter le répertoire racine au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.image_models import db

def init_database():
    """Initialise la base de données."""
    print("🗄️ Initialisation de la base de données...")

    # Créer les dossiers nécessaires
    os.makedirs('instance', exist_ok=True)
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('logs', exist_ok=True)

    try:
        app = create_app('development')
        with app.app_context():
            # Supprimer les tables existantes et les recréer
            db.drop_all()
            db.create_all()
            print("✅ Base de données créée avec succès")
            print(f"📁 Fichier de base: instance/app.db")

    except Exception as e:
        print(f"❌ Erreur: {e}")
        print("\n💡 Solutions possibles:")
        print("1. Vérifiez que le dossier 'instance' existe")
        print("2. Vérifiez les permissions d'écriture")
        print("3. Supprimez le fichier instance/app.db s'il existe")
        return False

    return True

if __name__ == "__main__":
    success = init_database()
    if success:
        print("\n🚀 Vous pouvez maintenant démarrer l'application avec: python run.py")
    else:
        sys.exit(1)
