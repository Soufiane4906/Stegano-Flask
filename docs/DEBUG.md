# 🔧 Guide de Debug - Problèmes de Base de Données

## Problème Actuel
```
sqlite3.OperationalError: unable to open database file
```

## Solutions par Étapes

### 1. Vérification de Base

```bash
# Activer l'environnement virtuel
venv\Scripts\activate.bat

# Vérifier le répertoire actuel
echo %CD%

# Créer les dossiers manuellement
mkdir instance
mkdir uploads
mkdir logs

# Vérifier que les dossiers existent
dir instance
```

### 2. Test de l'Application Simple

```bash
# Tester sans base de données
python run_simple.py
```

Visitez http://localhost:5000 - l'application devrait fonctionner.

### 3. Initialisation de la Base de Données

```bash
# Script d'initialisation dédié
python init_db.py
```

### 4. Configuration Alternative

Modifiez `.env` pour utiliser un chemin absolu :

```env
DATABASE_URL=sqlite:///C:/Users/Soufiane/source/repos/SF/Stegano-Flask/instance/app.db
```

### 5. Test Rapide de SQLite

```bash
# Tester SQLite directement
python -c "import sqlite3; conn = sqlite3.connect('instance/test.db'); print('SQLite OK'); conn.close()"
```

## Solutions de Contournement

### Option A: Désactiver la Base de Données

Modifiez `app/__init__.py` pour ignorer la base :

```python
# Commentez la création de la base
# with app.app_context():
#     db.create_all()
```

### Option B: Utiliser une Base en Mémoire

Modifiez `.env` :

```env
DATABASE_URL=sqlite:///:memory:
```

### Option C: Mode Développement Sans DB

Utilisez `run_simple.py` pour les tests de base.

## Vérifications

1. ✅ Python fonctionne
2. ✅ Flask installé
3. ✅ Stegano installé
4. ✅ Pillow installé
5. ❌ Base de données (problème actuel)

## Prochaines Étapes

1. Tester `python run_simple.py`
2. Si ça marche, corriger la base de données
3. Puis tester `python run.py`

## Commandes de Debug

```bash
# Lancer les tests
.\test_app.bat

# Ou manuellement
venv\Scripts\activate.bat
python run_simple.py
```
