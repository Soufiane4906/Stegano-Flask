#!/usr/bin/env python3
"""
Test simple pour vérifier les uploads avec curl
"""

import subprocess
import os

def test_upload_endpoints():
    """Test les endpoints d'upload avec curl"""

    # Vérifier qu'il y a des images de test
    test_images_dir = "test_images"
    if not os.path.exists(test_images_dir):
        print(f"❌ Dossier {test_images_dir} manquant")
        return

    # Chercher une image de test
    test_image = None
    for ext in ['png', 'jpg', 'jpeg']:
        for file in os.listdir(test_images_dir):
            if file.lower().endswith(ext):
                test_image = os.path.join(test_images_dir, file)
                break
        if test_image:
            break

    if not test_image:
        print("❌ Aucune image de test trouvée")
        return

    print(f"📸 Image de test trouvée: {test_image}")

    base_url = "http://localhost:5000"

    tests = [
        {
            "name": "AI Detection",
            "url": f"{base_url}/api/images/ai-detection",
            "field": "file"
        },
        {
            "name": "Hide Message",
            "url": f"{base_url}/api/images/hide",
            "field": "file",
            "extra": ["-F", "message=TestMessage"]
        }
    ]

    print("\n🧪 Test des uploads avec curl...")
    print("=" * 50)

    for test in tests:
        print(f"\n🔍 Test: {test['name']}")

        cmd = [
            "curl", "-X", "POST",
            "-F", f"{test['field']}=@{test_image}"
        ]

        if "extra" in test:
            cmd.extend(test["extra"])

        cmd.append(test["url"])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                print(f"✅ {test['name']}: Réponse reçue")
                print(f"📄 Réponse: {result.stdout[:200]}...")
            else:
                print(f"❌ {test['name']}: Erreur")
                print(f"📄 Erreur: {result.stderr}")

        except subprocess.TimeoutExpired:
            print(f"⏱️ {test['name']}: Timeout")
        except Exception as e:
            print(f"❌ {test['name']}: Exception: {e}")

    print("\n" + "=" * 50)
    print("✨ Tests terminés")

if __name__ == "__main__":
    print("🚀 Test des uploads d'images")
    print("💡 Assurez-vous que l'application est démarrée")
    print()

    test_upload_endpoints()
