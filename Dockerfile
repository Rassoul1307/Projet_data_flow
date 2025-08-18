# Image officielle Airflow
FROM apache/airflow:2.3.0

# Passage en root pour installer les dépendances
USER root

# Installation des dépendances système nécessaires
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc curl openjdk-11-jdk wget netcat \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


# Variables d'environnement Java et Spark - MODIFIÉES POUR 3.3.1
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV SPARK_VERSION=3.3.1
ENV HADOOP_VERSION=3
ENV HADOOP_FULL_VERSION=3.3.4
ENV SPARK_HOME=/opt/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}
ENV HADOOP_HOME=/opt/hadoop
ENV HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop
ENV YARN_CONF_DIR=/opt/hadoop/etc/hadoop
ENV PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin:$HADOOP_HOME/bin:$HADOOP_HOME/sbin

# Installer Spark 3.3.1 depuis l'archive Apache - MODIFIÉ
RUN curl -fsSL https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz -o /tmp/spark.tgz \
    && tar -xzf /tmp/spark.tgz -C /opt/ \
    && rm /tmp/spark.tgz

# Installer Hadoop (version légère pour les configs)
RUN curl -fsSL https://archive.apache.org/dist/hadoop/common/hadoop-${HADOOP_FULL_VERSION}/hadoop-${HADOOP_FULL_VERSION}.tar.gz -o /tmp/hadoop.tgz \
    && tar -xzf /tmp/hadoop.tgz -C /opt/ \
    && mv /opt/hadoop-${HADOOP_FULL_VERSION} /opt/hadoop \
    && rm /tmp/hadoop.tgz

# Créer les répertoires de configuration
RUN mkdir -p ${HADOOP_CONF_DIR}



# Téléchargement des JARs Spark-Kafka 
RUN mkdir -p /opt/spark-jars && \
    cd /opt/spark-jars && \
    echo "Téléchargement des JARs Spark-Kafka..." && \
    # JARs principaux pour Spark-Kafka
    curl -fsSL -o spark-sql-kafka-0-10_2.12-3.3.1.jar \
        "https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.12/3.3.1/spark-sql-kafka-0-10_2.12-3.3.1.jar" && \
    curl -fsSL -o spark-token-provider-kafka-0-10_2.12-3.3.1.jar \
        "https://repo1.maven.org/maven2/org/apache/spark/spark-token-provider-kafka-0-10_2.12/3.3.1/spark-token-provider-kafka-0-10_2.12-3.3.1.jar" && \
    curl -fsSL -o kafka-clients-2.8.1.jar \
        "https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/2.8.1/kafka-clients-2.8.1.jar" && \
    # JARs Hadoop
    curl -fsSL -o hadoop-client-runtime-3.3.2.jar \
        "https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-client-runtime/3.3.2/hadoop-client-runtime-3.3.2.jar" && \
    curl -fsSL -o hadoop-client-api-3.3.2.jar \
        "https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-client-api/3.3.2/hadoop-client-api-3.3.2.jar" && \
    # JARs utilitaires
    curl -fsSL -o lz4-java-1.8.0.jar \
        "https://repo1.maven.org/maven2/org/lz4/lz4-java/1.8.0/lz4-java-1.8.0.jar" && \
    curl -fsSL -o snappy-java-1.1.8.4.jar \
        "https://repo1.maven.org/maven2/org/xerial/snappy/snappy-java/1.1.8.4/snappy-java-1.1.8.4.jar" && \
    curl -fsSL -o slf4j-api-1.7.32.jar \
        "https://repo1.maven.org/maven2/org/slf4j/slf4j-api/1.7.32/slf4j-api-1.7.32.jar" && \
    curl -fsSL -o commons-logging-1.1.3.jar \
        "https://repo1.maven.org/maven2/commons-logging/commons-logging/1.1.3/commons-logging-1.1.3.jar" && \
    curl -fsSL -o jsr305-3.0.0.jar \
        "https://repo1.maven.org/maven2/com/google/code/findbugs/jsr305/3.0.0/jsr305-3.0.0.jar" && \
    curl -fsSL -o commons-pool2-2.11.1.jar \
        "https://repo1.maven.org/maven2/org/apache/commons/commons-pool2/2.11.1/commons-pool2-2.11.1.jar" && \
    echo "Vérification des téléchargements..." && \
    ls -la /opt/spark-jars/ && \
    echo "Téléchargement des JARs terminé avec succès"

# Créer un script pratique pour utiliser les JARs pré-téléchargés
RUN echo '#!/bin/bash\nspark-submit --master yarn --jars /opt/spark-jars/*.jar "$@"' > /usr/local/bin/spark-submit-with-jars && \
    chmod +x /usr/local/bin/spark-submit-with-jars && \
    echo "Script spark-submit-with-jars créé"



# Donner les permissions à l'utilisateur airflow
RUN chown -R airflow:root /opt/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} \
    && chown -R airflow:root /opt/hadoop \
    && chown -R airflow:root /opt/spark-jars \
    && chown airflow:root /usr/local/bin/spark-submit-with-jars

# Retour à l'utilisateur airflow
USER airflow

# Installation des dépendances Python nécessaires
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt