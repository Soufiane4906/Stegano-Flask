# 🚀 Démarrage Rapide - Stegano-Flask v2.0

## Installation Express (Windows)

### Option 1: Installation Simple (Recommandée)

```bash
# 1. Activer l'environnement virtuel
venv\Scripts\activate.bat

# 2. Mettre à jour les outils de base
python -m pip install --upgrade pip setuptools wheel

# 3. Installer les essentiels (un par un)
pip install Flask==3.0.0
pip install Flask-Cors==4.0.0
pip install Flask-SQLAlchemy==3.1.1
pip install python-dotenv==1.0.0
pip install Pillow
pip install stegano

# 4. Créer la configuration
copy .env.example .env

# 5. Créer les dossiers
mkdir instance uploads logs

# 6. Tester
python run.py
```

### Option 2: Script Automatique Fixé

```bash
# Lancer le script d'installation simple
.\install_simple.bat
```

## Si Vous Avez des Erreurs

### Erreur Flask non trouvé
```bash
venv\Scripts\activate.bat
pip install Flask
python -c "import flask; print('Flask OK')"
```

### Erreur NumPy
```bash
pip install --only-binary=all numpy
```

### Erreur TensorFlow/OpenCV
Ignorez ces packages pour l'instant - ils sont optionnels:
```bash
# L'app peut fonctionner sans IA
# Modifiez .env : AI_MODEL_PATH=
```

## Test Rapide

```bash
# 1. Vérifier l'environnement
venv\Scripts\activate.bat

# 2. Tester les imports
python -c "from app import create_app; print('App OK')"

# 3. Lancer l'app
python run.py
```

## Fonctionnalités Minimales

Même sans toutes les dépendances, vous aurez :
✅ API REST fonctionnelle
✅ Upload d'images
✅ Stéganographie (avec stegano)
✅ Métadonnées d'images
❌ Détection IA (nécessite TensorFlow)
❌ Recherche d'images similaires (nécessite opencv)

## Démarrer Sans IA

Modifiez `.env` :
```
AI_MODEL_PATH=
```

L'application démarrera sans les fonctionnalités IA.

## 🆘 Si Problème Persistant

Voir **TROUBLESHOOTING.md** pour le guide détaillé.
