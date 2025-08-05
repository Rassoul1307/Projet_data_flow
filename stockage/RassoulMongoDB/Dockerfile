FROM python:3.11-slim

# Définir le dossier de travail
WORKDIR /app

# Copier les fichiers principaux dans l'image
COPY requirements.txt .
COPY creation_stockage_mongo.py .

# Installer les dépendances
RUN pip install -r requirements.txt

# Copier les données dans un dossier indépendant
COPY data/ /data/

# Lancer le script
CMD ["python", "creation_stockage_mongo.py"]