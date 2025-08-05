FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers
COPY . .

RUN chmod +x wait-for-cassandra.sh

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt



# Lancer le script
CMD ["python", "insert_db.py"]
