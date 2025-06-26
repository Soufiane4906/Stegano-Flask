# Guide d'installation Python 3.10 pour TensorFlow

## Problème actuel
- TensorFlow nécessite Python 3.9-3.11 (recommandé : 3.10)
- Python 3.9 semble corrompu sur votre système
- Python 3.13 est trop récent pour TensorFlow

## Solution : Installer Python 3.10

### Étape 1 : Télécharger Python 3.10
1. Allez sur https://www.python.org/downloads/release/python-31011/
2. Téléchargez "Windows installer (64-bit)" : python-3.10.11-amd64.exe

### Étape 2 : Installation
1. Exécutez python-3.10.11-amd64.exe
2. ✅ Cochez "Add Python to PATH"
3. Cliquez sur "Customize installation"
4. ✅ Cochez toutes les "Optional Features"
5. Dans "Advanced Options" :
   - ✅ Install for all users
   - ✅ Add Python to environment variables
   - ✅ Precompile standard library
   - Installation path : C:\Python310

### Étape 3 : Vérification
Après installation, ouvrez un nouveau terminal et tapez :
```
py -0
```
Vous devriez voir Python 3.10 dans la liste.

### Étape 4 : Création de l'environnement virtuel
```bash
cd "c:\Users\Soufiane\source\repos\SF\Stegano-Flask"
py -3.10 -m venv venv
venv\Scripts\activate
pip install --upgrade pip
```

### Étape 5 : Installation des dépendances avec TensorFlow
```bash
pip install tensorflow==2.15.0
pip install -r requirements.txt
```

## Alternative : Utiliser Python 3.12 (si TensorFlow est compatible)
Si vous préférez ne pas installer Python 3.10, nous pouvons tester avec Python 3.12 :
```bash
py -3.12 -m venv venv
venv\Scripts\activate
pip install --upgrade pip
pip install tensorflow
```

## Vérification de TensorFlow
Après installation :
```python
import tensorflow as tf
print(f"TensorFlow version: {tf.__version__}")
print(f"Python version: {tf.python.sys.version}")
```
