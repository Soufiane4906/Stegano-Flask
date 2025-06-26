FROM python:3.9-slim

# Métadonnées
LABEL maintainer="Stegano-Flask Team"
LABEL version="2.0.0"
LABEL description="API Flask pour l'analyse d'images et la détection de stéganographie"

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production

# Répertoire de travail
WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de requirements
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY . .

# Créer les dossiers nécessaires
RUN mkdir -p uploads instance logs

# Exposer le port
EXPOSE 5000

# Créer un utilisateur non-root
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Commande de démarrage
CMD ["python", "run.py"]
