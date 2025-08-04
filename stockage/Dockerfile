FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances
COPY stockage/requirements.txt .
RUN pip install -r requirements.txt

# Copier le script Python
COPY stockage/creation_stockage_mongo.py .

# Copier les données
COPY data/ ./data/

# Lancer le script
CMD ["python", "creation_stockage_mongo.py"]