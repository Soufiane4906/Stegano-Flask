#!/usr/bin/env python3
"""
Point d'entrée principal pour l'application Flask de stéganographie.
"""

import os
from app import create_app

# Déterminer l'environnement
config_name = os.environ.get('FLASK_ENV', 'development')

# Créer l'application
app = create_app(config_name)

if __name__ == '__main__':
    # Configuration pour le développement
    debug = config_name == 'development'
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '127.0.0.1')

    print(f"🚀 Démarrage de l'application en mode {config_name}")
    print(f"📍 Accessible sur http://{host}:{port}")

    app.run(
        debug=debug,
        host=host,
        port=port,
        threaded=True
    )
