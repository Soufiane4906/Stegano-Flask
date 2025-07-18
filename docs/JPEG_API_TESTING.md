# 🧪 Guide de Test des API JPEG Steganography

Ce document contient des exemples pratiques pour tester les endpoints de l'API JPEG avec cURL et Insomnia.

## 📋 Prérequis

1. **Application démarrée** : `python run.py`
2. **Port par défaut** : `5000`
3. **URL de base** : `http://localhost:5000/api/v2/jpeg`
4. **Images de test** : Placez des images JPEG dans le dossier `test_images/`

## 🔧 Tests avec cURL

### 1. 📊 Analyser la capacité d'une image

```bash
# Analyser la capacité de dissimulation
curl -X POST http://localhost:5000/api/v2/jpeg/analyze_capacity \
  -F "file=@test_images/test_image_1.jpg" \
  -H "Content-Type: multipart/form-data"
```

**Réponse attendue :**
```json
{
  "success": true,
  "filename": "test_image_1.jpg",
  "capacity_analysis": {
    "exif_capacity": 32768,
    "lsb_capacity": 15000,
    "image_info": {
      "width": 194,
      "height": 259,
      "format": "JPEG"
    }
  }
}
```

### 2. 🔐 Cacher un message (méthode EXIF)

```bash
# Cacher un message dans les métadonnées EXIF
curl -X POST http://localhost:5000/api/v2/jpeg/hide_message \
  -F "file=@test_images/test_image_1.jpg" \
  -F "message=Ceci est un message secret caché dans EXIF ! 🔒" \
  -F "method=exif" \
  -H "Content-Type: multipart/form-data"
```

**Réponse attendue :**
```json
{
  "success": true,
  "message": "Message caché avec succès",
  "input_filename": "test_image_1.jpg",
  "output_filename": "test_image_1_stego_exif.jpg",
  "method": "exif",
  "message_length": 55,
  "details": {
    "method": "exif",
    "message_length": 55
  }
}
```

### 3. 🔢 Cacher un message (méthode LSB)

```bash
# Cacher un message avec la méthode LSB
curl -X POST http://localhost:5000/api/v2/jpeg/hide_message \
  -F "file=@test_images/test_image_3.jpg" \
  -F "message=Message plus long pour tester LSB. Cette méthode permet de cacher plus de données en modifiant les bits de poids faible des pixels." \
  -F "method=lsb" \
  -H "Content-Type: multipart/form-data"
```

### 4. 🔍 Extraire un message caché

```bash
# Extraire un message EXIF
curl -X POST http://localhost:5000/api/v2/jpeg/extract_message \
  -F "file=@uploads/test_image_1_stego_exif.jpg" \
  -F "method=exif" \
  -H "Content-Type: multipart/form-data"
```

**Réponse attendue :**
```json
{
  "success": true,
  "filename": "test_image_1_stego_exif.jpg",
  "method": "exif",
  "message_found": true,
  "message": "Ceci est un message secret caché dans EXIF ! 🔒",
  "message_length": 55
}
```

### 5. ✍️ Créer une signature stéganographique

```bash
# Créer une signature pour vérifier l'intégrité
curl -X POST http://localhost:5000/api/v2/jpeg/create_signature \
  -F "file=@test_images/test_image_1.jpg" \
  -H "Content-Type: multipart/form-data"
```

### 6. ✅ Vérifier une signature

```bash
# Vérifier l'intégrité d'une image signée
curl -X POST http://localhost:5000/api/v2/jpeg/verify_signature \
  -F "file=@uploads/test_image_1_signed.jpg" \
  -H "Content-Type: multipart/form-data"
```

### 7. 📚 Obtenir les méthodes disponibles

```bash
# Lister toutes les méthodes disponibles
curl -X GET http://localhost:5000/api/v2/jpeg/methods \
  -H "Content-Type: application/json"
```

## 🚀 Collection Insomnia

### Configuration de l'environnement Insomnia

1. **Créer un environnement** avec les variables suivantes :

```json
{
  "base_url": "http://localhost:5000",
  "api_path": "/api/v2/jpeg"
}
```

### Requêtes Insomnia à importer

#### 1. Analyze Capacity
- **Méthode** : `POST`
- **URL** : `{{ _.base_url }}{{ _.api_path }}/analyze_capacity`
- **Body** : `Multipart Form`
  - `file` : [File] Sélectionner une image JPEG

#### 2. Hide Message - EXIF
- **Méthode** : `POST`
- **URL** : `{{ _.base_url }}{{ _.api_path }}/hide_message`
- **Body** : `Multipart Form`
  - `file` : [File] Image JPEG
  - `message` : [Text] `Secret message in EXIF! 🔐`
  - `method` : [Text] `exif`

#### 3. Hide Message - LSB
- **Méthode** : `POST`
- **URL** : `{{ _.base_url }}{{ _.api_path }}/hide_message`
- **Body** : `Multipart Form`
  - `file` : [File] Image JPEG
  - `message` : [Text] `Longer message for LSB testing with more capacity...`
  - `method` : [Text] `lsb`

#### 4. Extract Message
- **Méthode** : `POST`
- **URL** : `{{ _.base_url }}{{ _.api_path }}/extract_message`
- **Body** : `Multipart Form`
  - `file` : [File] Image avec message caché
  - `method` : [Text] `exif` ou `lsb`

#### 5. Create Signature
- **Méthode** : `POST`
- **URL** : `{{ _.base_url }}{{ _.api_path }}/create_signature`
- **Body** : `Multipart Form`
  - `file` : [File] Image JPEG

#### 6. Verify Signature
- **Méthode** : `POST`
- **URL** : `{{ _.base_url }}{{ _.api_path }}/verify_signature`
- **Body** : `Multipart Form`
  - `file` : [File] Image signée

#### 7. Get Methods
- **Méthode** : `GET`
- **URL** : `{{ _.base_url }}{{ _.api_path }}/methods`
- **Body** : Aucun

## 🧪 Scénarios de test complets

### Scénario 1 : Test EXIF complet

```bash
# 1. Analyser l'image
curl -X POST http://localhost:5000/api/v2/jpeg/analyze_capacity \
  -F "file=@test_images/test_image_1.jpg"

# 2. Cacher un message
curl -X POST http://localhost:5000/api/v2/jpeg/hide_message \
  -F "file=@test_images/test_image_1.jpg" \
  -F "message=Test EXIF complet 🔒" \
  -F "method=exif"

# 3. Extraire le message
curl -X POST http://localhost:5000/api/v2/jpeg/extract_message \
  -F "file=@uploads/test_image_1_stego_exif.jpg" \
  -F "method=exif"
```

### Scénario 2 : Test LSB complet

```bash
# 1. Analyser une image plus grande
curl -X POST http://localhost:5000/api/v2/jpeg/analyze_capacity \
  -F "file=@test_images/test_image_3.jpg"

# 2. Cacher un message long
curl -X POST http://localhost:5000/api/v2/jpeg/hide_message \
  -F "file=@test_images/test_image_3.jpg" \
  -F "message=Message long pour tester LSB avec plus de capacité. Cette méthode permet de cacher beaucoup plus de données que EXIF." \
  -F "method=lsb"

# 3. Extraire le message
curl -X POST http://localhost:5000/api/v2/jpeg/extract_message \
  -F "file=@uploads/test_image_3_stego_lsb.jpg" \
  -F "method=lsb"
```

### Scénario 3 : Test de signature et intégrité

```bash
# 1. Créer une signature
curl -X POST http://localhost:5000/api/v2/jpeg/create_signature \
  -F "file=@test_images/test_image_1.jpg"

# 2. Vérifier la signature
curl -X POST http://localhost:5000/api/v2/jpeg/verify_signature \
  -F "file=@uploads/test_image_1_signed.jpg"
```

## 🔧 Scripts d'automatisation

### Script Bash pour tests automatiques

```bash
#!/bin/bash
# test_jpeg_api.sh

BASE_URL="http://localhost:5000/api/v2/jpeg"
TEST_IMAGE="test_images/test_image_1.jpg"

echo "🧪 Tests automatiques de l'API JPEG Steganography"
echo "=================================================="

# Test 1: Analyser la capacité
echo "📊 Test 1: Analyse de capacité..."
curl -s -X POST "$BASE_URL/analyze_capacity" \
  -F "file=@$TEST_IMAGE" | jq .

echo -e "\n"

# Test 2: Cacher un message EXIF
echo "🔐 Test 2: Dissimulation EXIF..."
curl -s -X POST "$BASE_URL/hide_message" \
  -F "file=@$TEST_IMAGE" \
  -F "message=Message test automatique EXIF 🤖" \
  -F "method=exif" | jq .

echo -e "\n"

# Test 3: Extraire le message
echo "🔍 Test 3: Extraction EXIF..."
curl -s -X POST "$BASE_URL/extract_message" \
  -F "file=@uploads/test_image_1_stego_exif.jpg" \
  -F "method=exif" | jq .

echo -e "\n✅ Tests terminés!"
```

### Script PowerShell pour Windows

```powershell
# test_jpeg_api.ps1

$BaseUrl = "http://localhost:5000/api/v2/jpeg"
$TestImage = "test_images/test_image_1.jpg"

Write-Host "🧪 Tests automatiques de l'API JPEG Steganography" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green

# Test 1: Analyser la capacité
Write-Host "📊 Test 1: Analyse de capacité..." -ForegroundColor Yellow
$response1 = Invoke-RestMethod -Uri "$BaseUrl/analyze_capacity" -Method Post -Form @{
    file = Get-Item $TestImage
}
$response1 | ConvertTo-Json -Depth 4

# Test 2: Cacher un message
Write-Host "🔐 Test 2: Dissimulation EXIF..." -ForegroundColor Yellow
$response2 = Invoke-RestMethod -Uri "$BaseUrl/hide_message" -Method Post -Form @{
    file = Get-Item $TestImage
    message = "Message test PowerShell 🔒"
    method = "exif"
}
$response2 | ConvertTo-Json -Depth 4

Write-Host "✅ Tests terminés!" -ForegroundColor Green
```

## 🎯 Conseils de test

1. **Préparez vos images** : Placez plusieurs images JPEG dans `test_images/`
2. **Vérifiez les permissions** : Assurez-vous que le dossier `uploads/` est accessible en écriture
3. **Testez différentes tailles** : Petites images pour EXIF, grandes pour LSB
4. **Utilisez jq** : `curl ... | jq .` pour formater le JSON
5. **Vérifiez les logs** : Consultez les logs de l'application en cas d'erreur

## ❗ Gestion d'erreurs communes

### Erreur 400 - Fichier manquant
```json
{"error": "Aucun fichier fourni"}
```
**Solution** : Vérifiez que le paramètre `file` contient bien un fichier.

### Erreur 500 - Service indisponible
```json
{"error": "Erreur lors de la dissimulation: ..."}
```
**Solution** : Vérifiez les logs de l'application et le service JPEG.

### Fichier non trouvé
**Solution** : Vérifiez le chemin du fichier et les permissions.
