# API Documentation - Stegano-Flask v2.0

## Vue d'ensemble

L'API Stegano-Flask v2.0 est une API RESTful moderne pour l'analyse d'images, incluant la détection de stéganographie et la détection d'images générées par IA.

## URL de base

```
http://localhost:5000/api
```

## Endpoints

### 1. Analyse complète d'image

**POST** `/api/images/upload`

Effectue une analyse complète d'une image incluant la détection de stéganographie, la détection IA, l'extraction de métadonnées et la recherche d'images similaires.

**Paramètres:**
- `file` (form-data): Fichier image à analyser

**Réponse:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "filename": "abc123.png",
    "image_path": "uploads/abc123.png",
    "metadata": {
      "dimensions": "1024x768",
      "width": 1024,
      "height": 768,
      "format": "PNG",
      "mode": "RGB",
      "size": "245.67 KB"
    },
    "steganography": {
      "signature_detected": true,
      "signature": "Message secret",
      "method": "LSB"
    },
    "ai_detection": {
      "is_ai_generated": false,
      "confidence": 23.45,
      "model_version": "TensorFlow v2.12.0"
    },
    "similar_images": [
      {
        "id": 5,
        "filename": "similar.jpg",
        "similarity": 0.89
      }
    ],
    "hashes": {
      "perceptual": "a1b2c3d4e5f6",
      "md5": "1234567890abcdef"
    }
  }
}
```

### 2. Ajouter une stéganographie

**POST** `/api/images/steganography/add`

Ajoute un message caché dans une image.

**Paramètres:**
- `file` (form-data): Fichier image
- `message` (form-data): Message à cacher

**Réponse:**
```json
{
  "success": true,
  "data": {
    "message": "Message caché ajouté avec succès",
    "original_image": "original.png",
    "steganography_image": "original_steg.png",
    "image_url": "/uploads/original_steg.png",
    "hidden_message": "Message secret"
  }
}
```

### 3. Détecter la stéganographie uniquement

**POST** `/api/images/steganography/detect`

Détecte uniquement la présence de messages cachés dans une image.

**Paramètres:**
- `file` (form-data): Fichier image à analyser

**Réponse:**
```json
{
  "success": true,
  "data": {
    "filename": "test.png",
    "steganography": {
      "signature_detected": true,
      "signature": "Message trouvé",
      "method": "LSB"
    }
  }
}
```

### 4. Détection IA uniquement

**POST** `/api/images/ai-detection`

Détecte uniquement si une image est générée par IA.

**Paramètres:**
- `file` (form-data): Fichier image à analyser

**Réponse:**
```json
{
  "success": true,
  "data": {
    "filename": "test.png",
    "ai_detection": {
      "is_ai_generated": true,
      "confidence": 87.65,
      "model_version": "TensorFlow v2.12.0"
    }
  }
}
```

### 5. Historique des analyses

**GET** `/api/images/history`

Récupère l'historique des analyses d'images.

**Paramètres de requête:**
- `limit` (optionnel): Nombre maximum de résultats (défaut: 50, max: 100)
- `user_id` (optionnel): ID utilisateur pour filtrer

**Réponse:**
```json
{
  "success": true,
  "data": {
    "analyses": [
      {
        "id": 1,
        "filename": "test.png",
        "original_filename": "mon_image.png",
        "dimensions": "800x600",
        "format": "PNG",
        "has_steganography": true,
        "is_ai_generated": false,
        "created_at": "2025-01-15T10:30:00Z"
      }
    ],
    "count": 1
  }
}
```

### 6. Récupération d'images

**GET** `/api/images/uploads/<filename>`

Récupère un fichier image téléchargé.

### 7. Vérification de santé

**GET** `/api/images/health`

Vérifie l'état de santé de l'API.

**Réponse:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "services": {
      "image_service": "OK",
      "ai_detection": "OK",
      "steganography": "OK"
    }
  }
}
```

## Codes d'erreur

- `400 Bad Request`: Requête malformée, paramètres manquants
- `413 Payload Too Large`: Fichier trop volumineux
- `500 Internal Server Error`: Erreur interne du serveur

**Format des erreurs:**
```json
{
  "error": "Description de l'erreur"
}
```

## Limitations

- Taille maximale de fichier: 16 MB
- Formats d'images supportés: PNG, JPG, JPEG, GIF, BMP, TIFF, WEBP
- Message de stéganographie: Maximum 1000 caractères
- Historique: Maximum 100 résultats par requête

## Authentification

L'authentification n'est pas encore implémentée dans cette version. Toutes les requêtes sont actuellement ouvertes.

## Exemples d'utilisation

### JavaScript (Fetch API)

```javascript
// Analyser une image
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('http://localhost:5000/api/images/upload', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => console.log(data));

// Ajouter une stéganographie
const stegFormData = new FormData();
stegFormData.append('file', fileInput.files[0]);
stegFormData.append('message', 'Mon message secret');

fetch('http://localhost:5000/api/images/steganography/add', {
  method: 'POST',
  body: stegFormData
})
.then(response => response.json())
.then(data => console.log(data));
```

### Python (requests)

```python
import requests

# Analyser une image
with open('image.png', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:5000/api/images/upload', files=files)
    print(response.json())

# Ajouter une stéganographie
with open('image.png', 'rb') as f:
    files = {'file': f}
    data = {'message': 'Message secret'}
    response = requests.post('http://localhost:5000/api/images/steganography/add',
                           files=files, data=data)
    print(response.json())
```

### cURL

```bash
# Analyser une image
curl -X POST -F "file=@image.png" http://localhost:5000/api/images/upload

# Ajouter une stéganographie
curl -X POST -F "file=@image.png" -F "message=Secret" \
     http://localhost:5000/api/images/steganography/add
```
