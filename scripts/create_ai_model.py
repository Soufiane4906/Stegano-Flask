#!/usr/bin/env python3
"""
Script pour créer un modèle IA compatible pour la détection d'images générées par IA.
Utilise un modèle pré-entraîné ou crée un modèle simple basé sur des caractéristiques.
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
import os

def create_simple_ai_detection_model():
    """
    Crée un modèle simple pour la détection d'images générées par IA.
    Ce modèle est basé sur des caractéristiques visuelles communes.
    """
    print("🤖 Création d'un modèle simple de détection IA...")

    # Architecture du modèle
    model = keras.Sequential([
        layers.Input(shape=(128, 128, 3)),

        # Couches de convolution pour extraire les caractéristiques
        layers.Conv2D(32, (3, 3), activation='relu'),
        layers.MaxPooling2D((2, 2)),

        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.MaxPooling2D((2, 2)),

        layers.Conv2D(128, (3, 3), activation='relu'),
        layers.MaxPooling2D((2, 2)),

        # Couches denses pour la classification
        layers.Flatten(),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(64, activation='relu'),
        layers.Dropout(0.3),

        # Couche de sortie (probabilité que l'image soit générée par IA)
        layers.Dense(1, activation='sigmoid')
    ])

    # Compilation du modèle
    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy']
    )

    print("✅ Modèle créé avec succès")
    print(f"📊 Paramètres du modèle: {model.count_params():,}")

    return model

def create_pretrained_ai_detection_model():
    """
    Crée un modèle basé sur un réseau pré-entraîné (MobileNetV2).
    Plus efficace que le modèle simple.
    """
    print("🤖 Création d'un modèle basé sur MobileNetV2...")

    # Charger le modèle pré-entraîné (sans les couches de classification)
    base_model = keras.applications.MobileNetV2(
        input_shape=(128, 128, 3),
        include_top=False,
        weights='imagenet'
    )

    # Geler les couches du modèle de base
    base_model.trainable = False

    # Ajouter nos propres couches de classification
    model = keras.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(64, activation='relu'),
        layers.Dropout(0.3),
        layers.Dense(1, activation='sigmoid')
    ])

    # Compilation du modèle
    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy']
    )

    print("✅ Modèle MobileNetV2 créé avec succès")
    print(f"📊 Paramètres du modèle: {model.count_params():,}")

    return model

def create_dummy_training_data():
    """
    Crée des données d'entraînement factices pour initialiser le modèle.
    """
    print("📊 Création de données d'entraînement factices...")

    # Générer des images factices
    x_train = np.random.random((100, 128, 128, 3)).astype(np.float32)
    y_train = np.random.randint(0, 2, (100, 1)).astype(np.float32)

    x_val = np.random.random((20, 128, 128, 3)).astype(np.float32)
    y_val = np.random.randint(0, 2, (20, 1)).astype(np.float32)

    return (x_train, y_train), (x_val, y_val)

def train_and_save_model(model, model_path="model_v2.h5"):
    """
    Entraîne le modèle avec des données factices et le sauvegarde.
    """
    print("🎯 Entraînement du modèle...")

    # Créer des données d'entraînement factices
    (x_train, y_train), (x_val, y_val) = create_dummy_training_data()

    # Entraîner le modèle (juste quelques epochs pour l'initialiser)
    history = model.fit(
        x_train, y_train,
        validation_data=(x_val, y_val),
        epochs=3,
        batch_size=16,
        verbose=1
    )

    # Sauvegarder le modèle
    model.save(model_path)
    print(f"💾 Modèle sauvegardé: {model_path}")

    return model

def main():
    """Fonction principale pour créer et sauvegarder le modèle."""
    print("🚀 Création d'un modèle IA pour la détection d'images générées par IA")
    print("=" * 60)

    try:
        # Option 1: Modèle simple
        print("\n1️⃣ Création du modèle simple...")
        simple_model = create_simple_ai_detection_model()
        train_and_save_model(simple_model, "model_simple.h5")

        # Option 2: Modèle basé sur MobileNetV2 (plus efficace)
        print("\n2️⃣ Création du modèle MobileNetV2...")
        pretrained_model = create_pretrained_ai_detection_model()
        train_and_save_model(pretrained_model, "model_mobilenet.h5")

        # Remplacer l'ancien modèle
        if os.path.exists("model.h5"):
            os.rename("model.h5", "model_old.h5")
            print("📦 Ancien modèle sauvegardé comme model_old.h5")

        # Utiliser le modèle MobileNetV2 comme modèle principal
        import shutil
        shutil.copy2("model_mobilenet.h5", "model.h5")
        print("✅ Nouveau modèle installé comme model.h5")

        print("\n🎉 Modèles créés avec succès!")
        print("📁 Fichiers disponibles:")
        print("   - model.h5 (modèle principal - MobileNetV2)")
        print("   - model_simple.h5 (modèle simple)")
        print("   - model_mobilenet.h5 (modèle MobileNetV2)")
        print("   - model_old.h5 (ancien modèle sauvegardé)")

    except Exception as e:
        print(f"❌ Erreur lors de la création du modèle: {e}")
        return False

    return True

if __name__ == "__main__":
    main()
