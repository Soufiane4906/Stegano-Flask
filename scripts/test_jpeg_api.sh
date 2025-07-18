#!/bin/bash
# Script de test rapide pour l'API JPEG Steganography

set -e  # Arrêter en cas d'erreur

BASE_URL="http://localhost:5000/api/v2/jpeg"
TEST_IMAGE="/test_outputs/test_lsb_hidden.jpg"
UPLOAD_DIR="uploads"

# Couleurs pour l'affichage
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🧪 Script de test pour l'API JPEG Steganography${NC}"
echo "=================================================="

# Fonction pour afficher les résultats
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

# Vérifier que l'application est lancée
echo -e "${YELLOW}🔍 Vérification de la disponibilité de l'API...${NC}"
if curl -s -f "$BASE_URL/methods" > /dev/null; then
    print_result 0 "API accessible"
else
    print_result 1 "API non accessible - Vérifiez que l'application est lancée"
    exit 1
fi

# Vérifier que l'image de test existe
if [ ! -f "$TEST_IMAGE" ]; then
    echo -e "${RED}❌ Image de test non trouvée: $TEST_IMAGE${NC}"
    echo "💡 Placez une image JPEG dans le dossier test_images/"
    exit 1
fi

# Test 1: Obtenir les méthodes disponibles
echo -e "\n${YELLOW}📚 Test 1: Méthodes disponibles${NC}"
curl -s "$BASE_URL/methods" | jq -r '.methods | keys[]' | while read method; do
    echo "  - $method"
done

# Test 2: Analyser la capacité
echo -e "\n${YELLOW}📊 Test 2: Analyse de capacité${NC}"
CAPACITY_RESULT=$(curl -s -X POST "$BASE_URL/analyze_capacity" \
    -F "file=@$TEST_IMAGE")

if echo "$CAPACITY_RESULT" | jq -e '.success' > /dev/null; then
    print_result 0 "Analyse de capacité réussie"
    EXIF_CAP=$(echo "$CAPACITY_RESULT" | jq -r '.capacity_analysis.exif_capacity // 0')
    LSB_CAP=$(echo "$CAPACITY_RESULT" | jq -r '.capacity_analysis.lsb_capacity // 0')
    echo "  📤 Capacité EXIF: $EXIF_CAP caractères"
    echo "  📤 Capacité LSB: $LSB_CAP caractères"
else
    print_result 1 "Échec de l'analyse de capacité"
    echo "$CAPACITY_RESULT" | jq '.error // .'
fi

# Test 3: Cacher un message EXIF
echo -e "\n${YELLOW}🔐 Test 3: Dissimulation EXIF${NC}"
HIDE_RESULT=$(curl -s -X POST "$BASE_URL/hide_message" \
    -F "file=@$TEST_IMAGE" \
    -F "message=Test automatique EXIF 🔒" \
    -F "method=exif")

if echo "$HIDE_RESULT" | jq -e '.success' > /dev/null; then
    print_result 0 "Dissimulation EXIF réussie"
    OUTPUT_FILE=$(echo "$HIDE_RESULT" | jq -r '.output_filename')
    echo "  📄 Fichier créé: $OUTPUT_FILE"

    # Test 4: Extraire le message EXIF
    echo -e "\n${YELLOW}🔍 Test 4: Extraction EXIF${NC}"
    if [ -f "$UPLOAD_DIR/$OUTPUT_FILE" ]; then
        EXTRACT_RESULT=$(curl -s -X POST "$BASE_URL/extract_message" \
            -F "file=@$UPLOAD_DIR/$OUTPUT_FILE" \
            -F "method=exif")

        if echo "$EXTRACT_RESULT" | jq -e '.success' > /dev/null; then
            print_result 0 "Extraction EXIF réussie"
            MESSAGE=$(echo "$EXTRACT_RESULT" | jq -r '.message // "Aucun message"')
            echo "  💬 Message extrait: $MESSAGE"
        else
            print_result 1 "Échec de l'extraction EXIF"
            echo "$EXTRACT_RESULT" | jq '.error // .'
        fi
    else
        print_result 1 "Fichier de sortie non trouvé: $UPLOAD_DIR/$OUTPUT_FILE"
    fi
else
    print_result 1 "Échec de la dissimulation EXIF"
    echo "$HIDE_RESULT" | jq '.error // .'
fi

# Test 5: Test LSB avec une image plus grande si disponible
LSB_TEST_IMAGE="test_images/test_image_3.jpg"
if [ -f "$LSB_TEST_IMAGE" ]; then
    echo -e "\n${YELLOW}🔢 Test 5: Dissimulation LSB${NC}"
    LSB_HIDE_RESULT=$(curl -s -X POST "$BASE_URL/hide_message" \
        -F "file=@$LSB_TEST_IMAGE" \
        -F "message=Message plus long pour tester LSB avec plus de capacité que EXIF." \
        -F "method=lsb")

    if echo "$LSB_HIDE_RESULT" | jq -e '.success' > /dev/null; then
        print_result 0 "Dissimulation LSB réussie"
        LSB_OUTPUT_FILE=$(echo "$LSB_HIDE_RESULT" | jq -r '.output_filename')
        echo "  📄 Fichier créé: $LSB_OUTPUT_FILE"
    else
        print_result 1 "Échec de la dissimulation LSB"
        echo "$LSB_HIDE_RESULT" | jq '.error // .'
    fi
fi

# Test 6: Test de signature
echo -e "\n${YELLOW}✍️ Test 6: Signature stéganographique${NC}"
SIGNATURE_RESULT=$(curl -s -X POST "$BASE_URL/create_signature" \
    -F "file=@$TEST_IMAGE")

if echo "$SIGNATURE_RESULT" | jq -e '.success' > /dev/null; then
    print_result 0 "Création de signature réussie"
    SIGNED_FILE=$(echo "$SIGNATURE_RESULT" | jq -r '.signed_filename')
    echo "  📄 Fichier signé: $SIGNED_FILE"

    # Vérifier la signature
    if [ -f "$UPLOAD_DIR/$SIGNED_FILE" ]; then
        VERIFY_RESULT=$(curl -s -X POST "$BASE_URL/verify_signature" \
            -F "file=@$UPLOAD_DIR/$SIGNED_FILE")

        if echo "$VERIFY_RESULT" | jq -e '.verification_result.verified' > /dev/null; then
            print_result 0 "Vérification de signature réussie"
        else
            print_result 1 "Échec de la vérification de signature"
        fi
    fi
else
    print_result 1 "Échec de la création de signature"
    echo "$SIGNATURE_RESULT" | jq '.error // .'
fi

echo -e "\n${GREEN}🎉 Tests terminés !${NC}"
echo "=================================================="

# Afficher les fichiers créés
echo -e "\n${YELLOW}📁 Fichiers créés dans $UPLOAD_DIR/:${NC}"
if [ -d "$UPLOAD_DIR" ]; then
    ls -la "$UPLOAD_DIR"/ | grep -E '\.(jpg|jpeg)$' || echo "  Aucun fichier JPEG trouvé"
else
    echo "  Dossier $UPLOAD_DIR non trouvé"
fi
