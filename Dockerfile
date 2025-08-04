# Image de base : Python 3.9 version légère
FROM python:3.9-slim

# Définit où on va travailler dans le conteneur
WORKDIR /app

# Copie d'abord le fichier des dépendances
# (Fait en premier pour optimiser le cache Docker)
COPY requirements.txt .

# Installation des packages Python nécessaires
RUN pip install --no-cache-dir -r requirements.txt

# Copie tout le reste du projet dans le conteneur
COPY . .

# Crée le dossier data au cas où il n'existerait pas
RUN mkdir -p data

# Port que l'application pourrait utiliser plus tard
# (Pas obligatoire pour ce projet mais bonne pratique)
EXPOSE 8000

# Commande par défaut (peut être surchargée par docker-compose)
CMD ["python", "scripts/import_data.py"]