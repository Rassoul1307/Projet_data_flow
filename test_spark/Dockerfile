FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers
COPY . .

# Installer les dépendances
RUN pip install --no-cache-dir pandas pymongo hdfs

# Commande de lancement
CMD ["python", "spark.py"]