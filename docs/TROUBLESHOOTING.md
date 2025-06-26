# Guide de Dépannage - Stegano-Flask v2.0

## 🚨 Problèmes d'Installation

### Erreur: "Cannot import 'setuptools.build_meta'"

**Cause**: Version de setuptools trop ancienne ou manquante.

**Solution**:
```bash
# Activer l'environnement virtuel
venv\Scripts\activate.bat

# Mettre à jour les outils de base
python -m pip install --upgrade pip setuptools wheel

# Réinstaller setuptools
pip install --force-reinstall setuptools
```

### Erreur: Compilation de NumPy échoue

**Cause**: NumPy essaie de se compiler depuis les sources au lieu d'utiliser des wheels pré-compilés.

**Solution**:
```bash
# Forcer l'utilisation de wheels pré-compilés
pip install --only-binary=all numpy

# Ou installer une version plus récente
pip install numpy>=1.24.0
```

### Erreur: "ModuleNotFoundError: No module named 'flask'"

**Cause**: Flask n'est pas installé dans l'environnement virtuel.

**Solution**:
```bash
# Vérifier que vous êtes dans l'environnement virtuel
venv\Scripts\activate.bat

# Installer Flask
pip install Flask==3.0.0

# Vérifier l'installation
python -c "import flask; print('Flask OK')"
```

## 🔧 Solutions par Étapes

### Option 1: Installation Minimale (Recommandée)

```bash
# 1. Activer l'environnement
venv\Scripts\activate.bat

# 2. Installer les essentiels
pip install -r requirements-minimal.txt

# 3. Tester
python run.py
```

### Option 2: Installation Progressive

```bash
# 1. Outils de base
pip install --upgrade pip setuptools wheel

# 2. Flask
pip install Flask Flask-Cors Flask-SQLAlchemy python-dotenv

# 3. Images (étape par étape)
pip install --only-binary=all Pillow
pip install --only-binary=all numpy
pip install stegano

# 4. Optionnel: OpenCV
pip install --only-binary=all opencv-python

# 5. Optionnel: IA (le plus problématique)
pip install tensorflow
```

### Option 3: Script Automatique

```bash
# Utiliser le script simplifié
.\install_simple.bat
```

## 🔍 Diagnostic

### Vérifier l'environnement virtuel

```bash
# Vérifier que vous êtes dans le bon environnement
echo %VIRTUAL_ENV%

# Devrait afficher quelque chose comme:
# C:\Users\...\Stegano-Flask\venv
```

### Vérifier les modules installés

```bash
# Lister les packages installés
pip list

# Vérifier Flask spécifiquement
python -c "import flask; print(flask.__version__)"
```

### Tester les imports

```bash
# Tester les imports un par un
python -c "import flask; print('Flask: OK')"
python -c "import numpy; print('NumPy: OK')"
python -c "import PIL; print('Pillow: OK')"
python -c "from stegano import lsb; print('Stegano: OK')"
```

## 🛠️ Solutions Spécifiques

### Pour TensorFlow (Optionnel)

Si TensorFlow pose problème, vous pouvez désactiver la détection IA :

1. **Modifier .env**:
   ```
   AI_MODEL_PATH=
   ```

2. **Ou commenter dans le code** (app/services/ai_detection_service.py):
   ```python
   # Désactiver temporairement TensorFlow
   # import tensorflow as tf
   ```

### Pour OpenCV (Optionnel)

Si OpenCV pose problème, vous pouvez utiliser seulement Pillow :

```bash
# Installer une version plus simple
pip install opencv-python-headless
```

### Problèmes de Permissions

```bash
# Si erreur de permissions
pip install --user <package>

# Ou relancer en administrateur
```

## 🔄 Réinitialisation Complète

Si tout échoue, recommencer à zéro :

```bash
# 1. Supprimer l'environnement virtuel
rmdir /s venv

# 2. Recréer
python -m venv venv
venv\Scripts\activate.bat

# 3. Installation minimale
pip install Flask python-dotenv Pillow stegano

# 4. Tester
python -c "from app import create_app; print('App OK')"
```

## 📋 Checklist de Vérification

- [ ] Python 3.9+ installé
- [ ] Environnement virtuel activé
- [ ] pip, setuptools, wheel à jour
- [ ] Flask installé et importable
- [ ] Fichier .env créé
- [ ] Dossiers instance/, uploads/, logs/ créés

## 💡 Conseils

1. **Toujours activer l'environnement virtuel** avant toute commande
2. **Installer les packages un par un** en cas de problème
3. **Utiliser --only-binary=all** pour éviter la compilation
4. **Commencer par requirements-minimal.txt** puis ajouter progressivement
5. **TensorFlow et OpenCV sont optionnels** - l'app peut fonctionner sans

## 🆘 Si Rien ne Fonctionne

Contactez-moi avec :
- Version de Python (`python --version`)
- Système d'exploitation
- Message d'erreur complet
- Résultat de `pip list`
