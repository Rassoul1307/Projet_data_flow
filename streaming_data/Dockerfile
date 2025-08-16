# Image officielle Airflow
FROM apache/airflow:2.3.0

# Passage en root pour installer les dépendances
USER root

# Installation des dépendances système si nécessaire
RUN apt-get update && apt-get install -y \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Retour à l'utilisateur airflow
USER airflow

# Installation des dépendances Python nécessaires
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# S'assurer que l'utilisateur airflow a les bonnes permissions
USER airflow