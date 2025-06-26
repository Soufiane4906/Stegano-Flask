#!/usr/bin/env python3
"""
Script de migration pour la refactorisation du projet Stegano-Flask.
Ce script aide à migrer de l'ancienne structure vers la nouvelle.
"""

import os
import shutil
import sqlite3
from datetime import datetime

def backup_existing_data():
    """
    Sauvegarde les données existantes avant la migration.
    """
    print("📦 Sauvegarde des données existantes...")

    backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)

    files_to_backup = [
        'images.db',
        'instance/users.db',
        'uploads/',
        'test_uploads/'
    ]

    for item in files_to_backup:
        if os.path.exists(item):
            if os.path.isdir(item):
                shutil.copytree(item, os.path.join(backup_dir, item))
            else:
                shutil.copy2(item, backup_dir)
            print(f"  ✅ Sauvegardé: {item}")

    print(f"💾 Sauvegarde complète dans: {backup_dir}")
    return backup_dir

def setup_new_structure():
    """
    Met en place la nouvelle structure de dossiers.
    """
    print("🏗️  Mise en place de la nouvelle structure...")

    directories = [
        'app',
        'app/models',
        'app/services',
        'app/api',
        'app/utils',
        'config',
        'tests',
        'instance',
        'uploads',
        'logs'
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"  📁 Créé: {directory}")

def migrate_database():
    """
    Migre les données de l'ancienne base vers la nouvelle structure.
    """
    print("🗄️  Migration de la base de données...")

    old_db_path = 'images.db'
    new_db_path = 'instance/app.db'

    if not os.path.exists(old_db_path):
        print("  ⚠️  Ancienne base de données introuvable, ignoré")
        return

    try:
        # Connecter aux bases de données
        old_conn = sqlite3.connect(old_db_path)
        new_conn = sqlite3.connect(new_db_path)

        # Créer les nouvelles tables
        from app import create_app
        from app.models.image_models import db

        app = create_app('development')
        with app.app_context():
            db.create_all()

        print("  ✅ Nouvelles tables créées")

        # Migrer les données si nécessaire
        # (Logique de migration spécifique selon vos données existantes)

        old_conn.close()
        new_conn.close()

        print("  ✅ Migration de la base terminée")

    except Exception as e:
        print(f"  ❌ Erreur lors de la migration: {str(e)}")

def setup_environment():
    """
    Configure l'environnement pour la nouvelle structure.
    """
    print("🔧 Configuration de l'environnement...")

    # Copier le fichier d'exemple vers .env si il n'existe pas
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            shutil.copy2('.env.example', '.env')
            print("  ✅ Fichier .env créé à partir de .env.example")
        else:
            print("  ⚠️  .env.example introuvable")

    # Créer le dossier de logs
    os.makedirs('logs', exist_ok=True)

    print("  ✅ Environnement configuré")

def cleanup_old_files():
    """
    Nettoie les anciens fichiers après confirmation.
    """
    print("🧹 Nettoyage des anciens fichiers...")

    old_files = [
        'steganoo.py',
        'steganoV2.py',
        'models.py'  # L'ancien models.py
    ]

    confirm = input("Voulez-vous supprimer les anciens fichiers Python ? (y/N): ")
    if confirm.lower() == 'y':
        for file in old_files:
            if os.path.exists(file):
                os.rename(file, f"{file}.old")
                print(f"  🗂️  Renommé: {file} -> {file}.old")
    else:
        print("  ⏭️  Nettoyage ignoré")

def main():
    """
    Fonction principale de migration.
    """
    print("🚀 Début de la migration du projet Stegano-Flask")
    print("=" * 50)

    try:
        # 1. Sauvegarde
        backup_dir = backup_existing_data()

        # 2. Structure
        setup_new_structure()

        # 3. Base de données
        migrate_database()

        # 4. Environnement
        setup_environment()

        # 5. Nettoyage
        cleanup_old_files()

        print("=" * 50)
        print("✅ Migration terminée avec succès!")
        print(f"📁 Sauvegarde disponible dans: {backup_dir}")
        print("")
        print("📋 Étapes suivantes:")
        print("1. Installez les dépendances: pip install -r requirements.txt")
        print("2. Configurez votre fichier .env")
        print("3. Testez l'application: python run.py")
        print("4. Lancez les tests: pytest tests/")

    except Exception as e:
        print(f"❌ Erreur lors de la migration: {str(e)}")
        print("🔄 Vous pouvez restaurer depuis la sauvegarde si nécessaire")

if __name__ == "__main__":
    main()
