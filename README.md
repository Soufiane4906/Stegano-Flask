# Stegano-Flask v2.0 🖼️🔍

Une API Flask moderne pour l'analyse d'images, incluant la détection de stéganographie et la détection d'images générées par IA.

## ✨ Fonctionnalités

### 🔍 Analyse d'images complète
- **Détection de stéganographie** : Détecte les messages cachés avec l'algorithme LSB
- **Détection d'images IA** : Identifie les images générées par intelligence artificielle
- **Extraction de métadonnées** : Dimensions, format, taille, etc.
- **Recherche de similitudes** : Trouve des images similaires avec hashing perceptuel
- **Détection de duplicatas** : Évite les doublons avec hashing MD5

### 🛠️ Fonctionnalités techniques
- **Architecture modulaire** avec Application Factory pattern
- **API RESTful** avec blueprints Flask
- **Base de données SQLAlchemy** pour l'historique
- **Validation robuste** des fichiers et données
- **Gestion d'erreurs complète**
- **Logging structuré**
- **Tests unitaires** avec pytest

## 🏗️ Architecture

```
stegano-flask/
├── app/                    # Application principale
│   ├── __init__.py        # Application factory
│   ├── models/            # Modèles de données
│   ├── services/          # Logique métier
│   ├── api/              # Endpoints API
│   └── utils/            # Utilitaires et validateurs
├── config/               # Configuration
├── tests/               # Tests unitaires
├── uploads/            # Fichiers téléchargés
├── instance/          # Base de données
└── run.py            # Point d'entrée
```

## 🚀 Installation et Configuration

### 1. Cloner le projet

```bash
git clone <repository-url>
cd Stegano-Flask
```

### 2. Créer un environnement virtuel

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configuration

```bash
# Copier le fichier de configuration d'exemple
cp .env.example .env

# Modifier .env selon vos besoins
nano .env
```

### 5. Migrer depuis l'ancienne version (optionnel)

Si vous avez une version précédente :

```bash
python migrate.py
```

### 6. Lancer l'application

```bash
python run.py
```

L'application sera disponible sur `http://localhost:5000`

## 📡 Utilisation de l'API

### Analyse complète d'une image

```bash
curl -X POST -F "file=@image.png" http://localhost:5000/api/images/upload
```

### Ajouter un message caché

```bash
curl -X POST -F "file=@image.png" -F "message=Secret" \
     http://localhost:5000/api/images/steganography/add
```

### Détecter la stéganographie

```bash
curl -X POST -F "file=@image.png" http://localhost:5000/api/images/steganography/detect
```

Voir [API_DOCUMENTATION.md](API_DOCUMENTATION.md) pour la documentation complète.

## 🧪 Tests

```bash
# Lancer tous les tests
pytest

# Avec couverture
pytest --cov=app

# Tests spécifiques
pytest tests/test_validators.py
```

## 📂 Structure des services

### SteganographyService
- Détection de messages cachés (LSB)
- Intégration de messages dans les images
- Calcul de hash perceptuel et MD5
- Recherche d'images similaires

### AIDetectionService
- Chargement du modèle TensorFlow
- Préprocessing des images
- Prédiction IA/Réel
- Traitement par lots

### ImageService
- Orchestration des analyses
- Gestion des fichiers
- Sauvegarde en base de données
- Historique des analyses

## ⚙️ Configuration

Variables d'environnement importantes :

```env
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///instance/app.db
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
AI_MODEL_PATH=modelFakeReal.h5
SIMILARITY_THRESHOLD=0.85
```

## 🔧 Développement

### Structure du code

- **Models** : Définition des tables de base de données
- **Services** : Logique métier réutilisable
- **API** : Endpoints REST avec validation
- **Utils** : Utilitaires, validateurs, exceptions

### Ajouter une nouvelle fonctionnalité

1. Créer le service dans `app/services/`
2. Ajouter les endpoints dans `app/api/`
3. Écrire les tests dans `tests/`
4. Mettre à jour la documentation

### Bonnes pratiques

- Utiliser les services pour la logique métier
- Valider toutes les entrées utilisateur
- Gérer les erreurs avec des exceptions personnalisées
- Logguer les opérations importantes
- Écrire des tests pour les nouvelles fonctionnalités

## 📊 Modèles de données

### User
- Authentification et profils utilisateur
- Relation avec les analyses d'images

### ImageAnalysis
- Historique des analyses
- Métadonnées et résultats
- Hashes pour déduplication

## 🛡️ Sécurité

- Validation stricte des fichiers
- Noms de fichiers sécurisés
- Limitation de taille des uploads
- Gestion des erreurs sans exposition d'informations sensibles

## 🔄 Migration depuis v1.x

Le script `migrate.py` aide à migrer depuis l'ancienne version :

1. Sauvegarde automatique des données
2. Création de la nouvelle structure
3. Migration de la base de données
4. Configuration de l'environnement

## 🐛 Résolution de problèmes

### Erreurs communes

**Modèle IA non trouvé** :
```bash
# Vérifier le chemin dans .env
AI_MODEL_PATH=modelFakeReal.h5
```

**Erreur de base de données** :
```bash
# Recréer la base
rm instance/app.db
python -c "from app import create_app; from app.models.image_models import db; app = create_app(); app.app_context().push(); db.create_all()"
```

**Problème de permissions** :
```bash
# Vérifier les permissions des dossiers
chmod 755 uploads/ instance/
```

## 📈 Performance

- Traitement asynchrone pour les analyses lourdes
- Cache des résultats de hash
- Optimisation des requêtes base de données
- Limitation du nombre de résultats

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🆕 Changelog

### v2.0.0
- Refactorisation complète avec architecture modulaire
- API RESTful avec blueprints
- Services séparés pour chaque fonctionnalité
- Base de données avec historique
- Tests unitaires
- Documentation complète
- Système de migration

### v1.x
- Version monolithique originale
- Fonctionnalités de base en un seul fichier
├── uploads/                # Folder to store uploaded images
├── venv/                   # Virtual environment folder
├── Include/
├── Lib/
├── Scripts/
│   ├── pyvenv.cfg
│   ├── .gitignore
├── app.py                  # Main Flask application file
├── model.h5                # Pre-trained TensorFlow model
├── models.py               # (Optional) Model-related code
├── realFake.ipynb          # (Optional) Jupyter notebook for model training/testing
├── steganoo.py             # (Optional) Steganography-related code
```

## Setup Instructions

### 1. Create a Virtual Environment

A virtual environment is used to isolate the project dependencies.

#### Windows
1. Open a terminal (Command Prompt or PowerShell).
2. Navigate to the project directory:
   ```
   cd path\to\FLASK-BACKEND
   ```
3. Create a virtual environment:
   ```
   python -m venv venv
   ```
4. Activate the virtual environment:
   ```
   venv\Scripts\activate
   ```

#### macOS/Linux
1. Open a terminal.
2. Navigate to the project directory:
   ```
   cd path/to/FLASK-BACKEND
   ```
3. Create a virtual environment:
   ```
   python3 -m venv venv
   ```
4. Activate the virtual environment:
   ```
   source venv/bin/activate
   ```

### 2. Install Dependencies

Install the required Python packages using the requirements.txt file.

1. Ensure the virtual environment is activated.
2. Run the following command:
   ```
   python -m pip install -r requirements.txt
   ```

### 3. Run the Flask Application

1. Ensure the virtual environment is activated.
2. Run the Flask application:
   ```
   python app.py
   ```
3. The application will start running at http://127.0.0.1:5000/.

## API Endpoints

### 1. Upload Image

- **Endpoint:** `/upload`
- **Method:** POST
- **Description:** Upload an image for steganography analysis, AI detection, and metadata extraction.
- **Request:**
  - Form-data:
    - `file`: The image file to upload.
- **Response:**
  ```json
  {
    "steganography": {
      "signature_detected": true/false,
      "signature": "hidden message" (if detected)
    },
    "ai_detection": {
      "is_ai_generated": true/false,
      "confidence": "confidence percentage"
    },
    "metadata": {
      "dimensions": "width x height",
      "format": "image format",
      "size": "file size in KB"
    },
    "image_path": "path to uploaded image"
  }
  ```

### 2. Add Hidden Signature

- **Endpoint:** `/add_steganography`
- **Method:** POST
- **Description:** Embed a hidden signature (message) into an image using steganography.
- **Request:**
  - Form-data:
    - `file`: The image file to embed the signature into.
    - `signature`: The hidden message to embed.
- **Response:**
  ```json
  {
    "message": "Signature ajoutée avec succès",
    "image_path": "path to the modified image"
  }
  ```

## Requirements

The requirements.txt file should include the following dependencies:

```
Flask==2.3.2
Flask-Cors==4.0.0
numpy==1.23.5
opencv-python==4.7.0.72
Pillow==9.5.0
stegano==0.9.4
tensorflow==2.12.0
```

## Troubleshooting

### 1. Model Not Loading
- Ensure the model.h5 file is present in the project directory.
- Verify the model's input shape matches the image preprocessing in detect_ai_image.

### 2. Dependency Issues
- Ensure the virtual environment is activated before installing dependencies.
- If TensorFlow installation fails, try installing a specific version compatible with your system.

### 3. Debugging
- Use the print statements in the code to debug issues (e.g., image shape before prediction).

## Example Usage

### Upload an Image
Use a tool like Postman or curl to send a POST request to `/upload` with an image file.

Example using curl:
```
curl -X POST -F "file=@image.png" http://127.0.0.1:5000/upload
```

### Add a Hidden Signature
Use a tool like Postman or curl to send a POST request to `/add_steganography` with an image file and a signature.

Example using curl:
```
curl -X POST -F "file=@image.png" -F "signature=HelloWorld" http://127.0.0.1:5000/add_steganography
```

## License

This project is open-source and available under the MIT License.

## Contact

For any questions or issues, please contact the project maintainer.
