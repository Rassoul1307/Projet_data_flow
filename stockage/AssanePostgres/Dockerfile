FROM python:3.11-slim

# Définir le dossier de travail dans le conteneur
WORKDIR /app

# Copier le dossier contenant app.py et requirements.txt
COPY app/ /app/

# Copier le fichier CSV (assure-toi qu'il est à la racine du projet)
COPY meteo_dakar_1000.csv /app/

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Définir la commande de démarrage du conteneur
CMD ["python", "app.py"]
