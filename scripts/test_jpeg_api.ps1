# Script PowerShell pour tester l'API JPEG Steganography
param(
    [string]$BaseUrl = "http://localhost:5000/api/v2/jpeg",
    [string]$TestImage = "test_images/test_image_1.jpg"
)

# Fonction pour afficher des messages colorés
function Write-ColoredOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Test-ApiEndpoint {
    param(
        [string]$Url,
        [hashtable]$Body = @{},
        [string]$Method = "GET"
    )

    try {
        if ($Method -eq "GET") {
            $response = Invoke-RestMethod -Uri $Url -Method $Method -ContentType "application/json"
        } else {
            $response = Invoke-RestMethod -Uri $Url -Method $Method -Form $Body
        }
        return @{ Success = $true; Data = $response }
    } catch {
        return @{ Success = $false; Error = $_.Exception.Message }
    }
}

Write-ColoredOutput "🧪 Script de test pour l'API JPEG Steganography" "Green"
Write-ColoredOutput "==================================================" "Green"

# Vérifier que l'application est lancée
Write-ColoredOutput "`n🔍 Vérification de la disponibilité de l'API..." "Yellow"
$methodsTest = Test-ApiEndpoint -Url "$BaseUrl/methods"

if ($methodsTest.Success) {
    Write-ColoredOutput "✅ API accessible" "Green"
} else {
    Write-ColoredOutput "❌ API non accessible - Vérifiez que l'application est lancée" "Red"
    Write-ColoredOutput "Erreur: $($methodsTest.Error)" "Red"
    exit 1
}

# Vérifier que l'image de test existe
if (-not (Test-Path $TestImage)) {
    Write-ColoredOutput "❌ Image de test non trouvée: $TestImage" "Red"
    Write-ColoredOutput "💡 Placez une image JPEG dans le dossier test_images/" "Yellow"
    exit 1
}

# Test 1: Obtenir les méthodes disponibles
Write-ColoredOutput "`n📚 Test 1: Méthodes disponibles" "Yellow"
if ($methodsTest.Success) {
    $methods = $methodsTest.Data.methods.PSObject.Properties.Name
    foreach ($method in $methods) {
        Write-ColoredOutput "  - $method" "White"
    }
    Write-ColoredOutput "✅ Récupération des méthodes réussie" "Green"
} else {
    Write-ColoredOutput "❌ Échec de la récupération des méthodes" "Red"
}

# Test 2: Analyser la capacité
Write-ColoredOutput "`n📊 Test 2: Analyse de capacité" "Yellow"
$capacityTest = Test-ApiEndpoint -Url "$BaseUrl/analyze_capacity" -Method "POST" -Body @{
    file = Get-Item $TestImage
}

if ($capacityTest.Success) {
    Write-ColoredOutput "✅ Analyse de capacité réussie" "Green"
    $exifCap = $capacityTest.Data.capacity_analysis.exif_capacity
    $lsbCap = $capacityTest.Data.capacity_analysis.lsb_capacity
    Write-ColoredOutput "  📤 Capacité EXIF: $exifCap caractères" "White"
    Write-ColoredOutput "  📤 Capacité LSB: $lsbCap caractères" "White"
} else {
    Write-ColoredOutput "❌ Échec de l'analyse de capacité" "Red"
    Write-ColoredOutput "Erreur: $($capacityTest.Error)" "Red"
}

# Test 3: Cacher un message EXIF
Write-ColoredOutput "`n🔐 Test 3: Dissimulation EXIF" "Yellow"
$hideTest = Test-ApiEndpoint -Url "$BaseUrl/hide_message" -Method "POST" -Body @{
    file = Get-Item $TestImage
    message = "Test automatique PowerShell EXIF 🔒"
    method = "exif"
}

if ($hideTest.Success) {
    Write-ColoredOutput "✅ Dissimulation EXIF réussie" "Green"
    $outputFile = $hideTest.Data.output_filename
    Write-ColoredOutput "  📄 Fichier créé: $outputFile" "White"

    # Test 4: Extraire le message EXIF
    $uploadPath = "uploads/$outputFile"
    if (Test-Path $uploadPath) {
        Write-ColoredOutput "`n🔍 Test 4: Extraction EXIF" "Yellow"
        $extractTest = Test-ApiEndpoint -Url "$BaseUrl/extract_message" -Method "POST" -Body @{
            file = Get-Item $uploadPath
            method = "exif"
        }

        if ($extractTest.Success) {
            Write-ColoredOutput "✅ Extraction EXIF réussie" "Green"
            $extractedMessage = $extractTest.Data.message
            Write-ColoredOutput "  💬 Message extrait: $extractedMessage" "White"
        } else {
            Write-ColoredOutput "❌ Échec de l'extraction EXIF" "Red"
            Write-ColoredOutput "Erreur: $($extractTest.Error)" "Red"
        }
    } else {
        Write-ColoredOutput "❌ Fichier de sortie non trouvé: $uploadPath" "Red"
    }
} else {
    Write-ColoredOutput "❌ Échec de la dissimulation EXIF" "Red"
    Write-ColoredOutput "Erreur: $($hideTest.Error)" "Red"
}

# Test 5: Test LSB avec une image plus grande si disponible
$lsbTestImage = "test_images/test_image_3.jpg"
if (Test-Path $lsbTestImage) {
    Write-ColoredOutput "`n🔢 Test 5: Dissimulation LSB" "Yellow"
    $lsbHideTest = Test-ApiEndpoint -Url "$BaseUrl/hide_message" -Method "POST" -Body @{
        file = Get-Item $lsbTestImage
        message = "Message plus long pour tester LSB avec plus de capacité que EXIF. Test PowerShell ! 🔢"
        method = "lsb"
    }

    if ($lsbHideTest.Success) {
        Write-ColoredOutput "✅ Dissimulation LSB réussie" "Green"
        $lsbOutputFile = $lsbHideTest.Data.output_filename
        Write-ColoredOutput "  📄 Fichier créé: $lsbOutputFile" "White"
    } else {
        Write-ColoredOutput "❌ Échec de la dissimulation LSB" "Red"
        Write-ColoredOutput "Erreur: $($lsbHideTest.Error)" "Red"
    }
} else {
    Write-ColoredOutput "`n⚠️ Image pour test LSB non trouvée: $lsbTestImage" "Yellow"
}

# Test 6: Test de signature
Write-ColoredOutput "`n✍️ Test 6: Signature stéganographique" "Yellow"
$signatureTest = Test-ApiEndpoint -Url "$BaseUrl/create_signature" -Method "POST" -Body @{
    file = Get-Item $TestImage
}

if ($signatureTest.Success) {
    Write-ColoredOutput "✅ Création de signature réussie" "Green"
    $signedFile = $signatureTest.Data.signed_filename
    Write-ColoredOutput "  📄 Fichier signé: $signedFile" "White"

    # Vérifier la signature
    $signedPath = "uploads/$signedFile"
    if (Test-Path $signedPath) {
        $verifyTest = Test-ApiEndpoint -Url "$BaseUrl/verify_signature" -Method "POST" -Body @{
            file = Get-Item $signedPath
        }

        if ($verifyTest.Success -and $verifyTest.Data.verification_result.verified) {
            Write-ColoredOutput "✅ Vérification de signature réussie" "Green"
        } else {
            Write-ColoredOutput "❌ Échec de la vérification de signature" "Red"
        }
    }
} else {
    Write-ColoredOutput "❌ Échec de la création de signature" "Red"
    Write-ColoredOutput "Erreur: $($signatureTest.Error)" "Red"
}

Write-ColoredOutput "`n🎉 Tests terminés !" "Green"
Write-ColoredOutput "==================================================" "Green"

# Afficher les fichiers créés
Write-ColoredOutput "`n📁 Fichiers créés dans uploads/:" "Yellow"
if (Test-Path "uploads") {
    $uploadedFiles = Get-ChildItem "uploads" -Filter "*.jpg"
    if ($uploadedFiles.Count -gt 0) {
        foreach ($file in $uploadedFiles) {
            Write-ColoredOutput "  📄 $($file.Name) ($($file.Length) bytes)" "White"
        }
    } else {
        Write-ColoredOutput "  Aucun fichier JPEG trouvé" "Gray"
    }
} else {
    Write-ColoredOutput "  Dossier uploads non trouvé" "Gray"
}

Write-ColoredOutput "`n💡 Conseils pour Insomnia:" "Cyan"
Write-ColoredOutput "1. Importez la collection: docs/insomnia_collection.json" "White"
Write-ColoredOutput "2. Configurez l'environnement avec base_url: http://localhost:5000" "White"
Write-ColoredOutput "3. Testez chaque endpoint avec vos propres images" "White"
