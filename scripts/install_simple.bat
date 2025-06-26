@echo off
chcp 65001 >nul
echo 🔧 Installation simple de Stegano-Flask v2.0
echo ============================================

REM Activer l'environnement virtuel
call venv\Scripts\activate.bat

echo 🧹 Nettoyage de l'environnement...
pip uninstall -y numpy opencv-python tensorflow pillow scikit-learn

echo 🛠️ Mise à jour des outils de base...
python -m pip install --upgrade pip setuptools wheel

echo 📦 Installation par étapes...

REM Étape 1: Flask et dépendances de base
echo [1/5] Flask et base...
pip install Flask==3.0.0 Flask-Cors==4.0.0 Flask-SQLAlchemy==3.1.1 python-dotenv==1.0.0 Werkzeug==3.0.0

REM Étape 2: NumPy (avec wheels pré-compilés)
echo [2/5] NumPy...
pip install --only-binary=all numpy

REM Étape 3: Pillow et OpenCV
echo [3/5] Pillow et OpenCV...
pip install --only-binary=all Pillow opencv-python

REM Étape 4: Stéganographie
echo [4/5] Stéganographie...
pip install stegano imagehash

REM Étape 5: Outils optionnels (peuvent échouer)
echo [5/5] Outils optionnels...
pip install scikit-learn bcrypt pytest pytest-flask || echo "⚠️ Outils optionnels non installés"

echo.
echo ✅ Installation de base terminée!
echo.
echo 💡 Pour TensorFlow (optionnel):
echo   pip install tensorflow
echo.
echo 🚀 Pour tester:
echo   python run.py
echo.

pause
