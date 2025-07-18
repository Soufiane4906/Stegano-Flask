@echo off
chcp 65001 >nul
title Interface de Test - JPEG Stéganographie

echo.
echo 🚀 Interface de Test - JPEG Stéganographie
echo ==========================================
echo.

REM Vérifier que Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installé ou pas dans le PATH
    echo 💡 Installez Python depuis https://python.org
    pause
    exit /b 1
)

REM Aller dans le dossier racine du projet
cd /d "%~dp0\.."

REM Vérifier que les dépendances sont installées
echo 🔍 Vérification des dépendances...
python -c "import flask, PIL" >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Installation des dépendances...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Erreur lors de l'installation des dépendances
        pause
        exit /b 1
    )
)

REM Créer les dossiers nécessaires
if not exist "uploads" mkdir uploads
if not exist "test_images" mkdir test_images
if not exist "logs" mkdir logs

echo ✅ Prêt à lancer l'interface de test
echo.
echo 📋 Informations:
echo   🌐 Interface: http://localhost:5000/test
echo   📊 API: http://localhost:5000/api/v2/jpeg
echo   📁 Images de test: test_images/
echo   📤 Fichiers générés: uploads/
echo.
echo 🎯 Instructions:
echo   1. L'interface va s'ouvrir dans votre navigateur
echo   2. Placez des images JPEG dans test_images/
echo   3. Testez les fonctionnalités de stéganographie
echo   4. Appuyez Ctrl+C pour arrêter
echo.

REM Lancer l'interface de test
python scripts/run_test_interface.py

echo.
echo ✅ Interface fermée
pause
