# Service de Stéganographie JPEG

Ce service fournit des fonctionnalités avancées de stéganographie spécialement conçues pour les images JPEG.

## Fonctionnalités

### 🔧 Méthodes de Stéganographie

1. **EXIF Steganography**
   - Cache les messages dans les métadonnées EXIF
   - Capacité : jusqu'à 32KB
   - Impact visuel : aucun
   - Détection : facile pour les outils d'analyse EXIF

2. **LSB (Least Significant Bit)**
   - Modifie les bits de poids faible des pixels
   - Capacité : variable selon la taille de l'image
   - Impact visuel : minimal
   - Détection : moyenne

3. **DCT (Discrete Cosine Transform)** *(en développement)*
   - Modifie les coefficients DCT
   - Capacité : variable
   - Impact visuel : faible
   - Détection : difficile

### 🛡️ Fonctionnalités de Sécurité

- **Signature Stéganographique** : Création de signatures pour vérifier l'intégrité
- **Analyse de Capacité** : Évaluation de la capacité de dissimulation
- **Validation d'Intégrité** : Détection des modifications

## Utilisation

### Installation des Dépendances

```bash
pip install pillow numpy
```

### Utilisation Basique

```python
from app.services.jpeg_steganography_service import JPEGSteganographyService

# Initialiser le service
service = JPEGSteganographyService()

# Analyser la capacité d'une image
capacity = service.analyze_jpeg_capacity("image.jpg")
print(f"Capacité LSB: {capacity['capacity_lsb_bytes']} bytes")

# Cacher un message
result = service.hide_message_in_jpeg(
    "image_source.jpg",
    "Mon message secret",
    "image_avec_message.jpg",
    method="exif"
)

# Extraire le message
extraction = service.extract_message_from_jpeg(
    "image_avec_message.jpg",
    method="exif"
)

if extraction['success'] and extraction['message']:
    print("Message trouvé:", extraction['message'])
```

### API REST

Le service est exposé via l'API REST sur `/api/v2/jpeg/` :

#### Analyser la Capacité
```http
POST /api/v2/jpeg/analyze_capacity
Content-Type: multipart/form-data

file: [fichier JPEG]
```

#### Cacher un Message
```http
POST /api/v2/jpeg/hide_message
Content-Type: multipart/form-data

file: [fichier JPEG]
message: "Votre message secret"
method: "exif" | "lsb" | "dct"
```

#### Extraire un Message
```http
POST /api/v2/jpeg/extract_message
Content-Type: multipart/form-data

file: [fichier JPEG avec message]
method: "exif" | "lsb" | "dct"
```

#### Créer une Signature
```http
POST /api/v2/jpeg/create_signature
Content-Type: multipart/form-data

file: [fichier JPEG]
```

#### Vérifier une Signature
```http
POST /api/v2/jpeg/verify_signature
Content-Type: multipart/form-data

file: [fichier JPEG signé]
```

#### Méthodes Disponibles
```http
GET /api/v2/jpeg/methods
```

## Tests

Pour tester le service :

```bash
# Depuis la racine du projet
python scripts/test_jpeg_steganography.py
```

### Exemple de Test Complet

```python
# Test complet avec une image JPEG
service = JPEGSteganographyService()

# 1. Analyser l'image
capacity = service.analyze_jpeg_capacity("test.jpg")
print("Analyse:", capacity)

# 2. Cacher un message
hide_result = service.hide_message_in_jpeg(
    "test.jpg",
    "Message de test 🔐",
    "test_stego.jpg",
    method="exif"
)

# 3. Extraire le message
extract_result = service.extract_message_from_jpeg(
    "test_stego.jpg",
    method="exif"
)

# 4. Créer une signature
signature_result = service.create_steganographic_signature(
    "test.jpg",
    "test_signed.jpg"
)

# 5. Vérifier l'intégrité
verification = service.verify_steganographic_signature("test_signed.jpg")
```

## Formats Supportés

- ✅ JPEG / JPG
- ❌ PNG (utiliser le service de stéganographie standard)
- ❌ GIF (non supporté)
- ❌ BMP (non supporté)

## Limitations

1. **Qualité JPEG** : Les méthodes LSB peuvent être affectées par la recompression JPEG
2. **Taille des Messages** : Limitée à 1MB par défaut
3. **Détection** : Les méthodes EXIF sont facilement détectables
4. **Compression** : La recompression JPEG peut altérer les messages LSB

## Recommandations

### Pour la Sécurité
- Utilisez la méthode DCT pour une meilleure résistance à la détection
- Évitez EXIF pour les données sensibles
- Testez toujours l'extraction après la dissimulation

### Pour la Performance
- Méthode EXIF : idéale pour les petits messages
- Méthode LSB : pour les messages de taille moyenne
- Analysez la capacité avant la dissimulation

### Pour la Qualité
- Utilisez des images de haute qualité (95%+)
- Évitez la recompression multiple
- Testez l'impact visuel

## Développements Futurs

- [ ] Implémentation complète de la méthode DCT
- [ ] Support de la compression adaptative
- [ ] Chiffrement automatique des messages
- [ ] Interface web dédiée
- [ ] Support de métadonnées personnalisées
- [ ] Optimisation pour les images de grande taille

## Sécurité

⚠️ **Avertissement** : Ce service est conçu à des fins éducatives et de recherche.

- Ne stockez pas de données sensibles sans chiffrement
- Testez en environnement sécurisé
- Respectez les lois locales sur la cryptographie
