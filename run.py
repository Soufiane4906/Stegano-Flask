#!/usr/bin/env python3
"""
Point d'entrée principal pour l'application Flask de stéganographie.
"""

import os
import sys
from app import create_app

def main():
    # Vérifier si l'utilisateur veut la version simple
    if len(sys.argv) > 1 and sys.argv[1] == '--simple':
        print("🔧 Démarrage en mode simple...")
        from app.simple_app import create_simple_app
        app = create_simple_app()
        config_name = 'simple'
    else:
        # Déterminer l'environnement
        config_name = os.environ.get('FLASK_ENV', 'development')
        # Créer l'application complète
        app = create_app(config_name)

    # Configuration pour le serveur
    debug = config_name in ['development', 'simple']
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '127.0.0.1')

    print(f"🚀 Démarrage de l'application en mode {config_name}")
    print(f"📍 Accessible sur http://{host}:{port}")

    if config_name == 'development':
        print("🔧 Mode développement activé")
        print("📁 Dossier uploads:", app.config['UPLOAD_FOLDER'])
        print("🔗 API disponible sur /api/v2/")
    elif config_name == 'simple':
        print("⚡ Mode simple activé")
        print("📁 Dossier uploads:", app.config['UPLOAD_FOLDER'])
        print("🔗 API simple disponible sur /api/v2/")

    app.run(
        debug=debug,
        host=host,
        port=port,
        threaded=True
    )

if __name__ == '__main__':
    main()
