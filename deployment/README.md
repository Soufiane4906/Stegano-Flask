# Déploiement

Ce dossier contient les fichiers de déploiement et d'orchestration :

- `Dockerfile` - Image Docker pour l'application
- `docker-compose.yml` - Orchestration multi-conteneurs

## Utilisation
```bash
# Construction de l'image
docker build -t stegano-flask .

# Démarrage avec docker-compose
docker-compose up -d
```
