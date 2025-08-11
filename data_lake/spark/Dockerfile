FROM bitnami/spark:3.5.0

USER root

# Installer pip et dépendances Python
RUN apt-get update && apt-get install -y python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Installer les librairies Python nécessaires
RUN pip3 install pyspark hdfs

# Créer dossier d'application
WORKDIR /app

# Copier ton script
COPY spark_app.py .

# Commande de lancement (tout en une seule liste)
CMD ["spark-submit","--packages","org.mongodb.spark:mongo-spark-connector_2.12:3.0.1,org.postgresql:postgresql:42.6.0,mysql:mysql-connector-java:8.0.33","spark_app.py"]