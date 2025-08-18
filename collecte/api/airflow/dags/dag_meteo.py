from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

#CONFIGURATION DE BASE 
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=3),
}

# CRÉATION DU DAG 
with DAG(
    dag_id='send_weather_to_kafka',
    default_args=default_args,
    description='Récupère les données météo et les envoie vers Kafka toutes les heures',
    schedule_interval=timedelta(hours=2),  
    start_date=datetime(2025, 8, 10),
    catchup=False,
    tags=['weather', 'kafka'],
) as dag:

    #  TÂCHE 1 : Lancer le producer météo 
    fetch_and_send_weather = BashOperator(
        task_id='fetch_and_send_weather',
        bash_command='cd /opt/airflow/scripts && python3 kafka/producer.py'
    )

    # TÂCHE 2 : Lancer le consumer vers logstash
    verify_pipeline = BashOperator(
        task_id='verify_pipeline',
        bash_command='''
            echo " Attente traitement Logstash..." && sleep 30 &&
            curl -s "http://elasticsearch:9200/_cat/indices/weather*" || echo "Pas encore d'index weather"
        ''',
        trigger_rule='all_done'  
    )

    # TÂCHE 3: Streaming Kafka vers HDFS (Data Lake)
    stream_to_hadoop = BashOperator(
        task_id='stream_hdfs',
        bash_command="""
/home/airflow/.local/bin/spark-submit \
  --master local[*] \
  --conf spark.hadoop.fs.defaultFS=hdfs://namenode:9000 \
  --conf spark.hadoop.dfs.client.use.datanode.hostname=true \
  --conf spark.sql.adaptive.enabled=false \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.1 \
  /opt/airflow/scripts/pyspark/streaming.py
""",
        trigger_rule='all_done'
    )
    
    # DÉPENDANCES 
    fetch_and_send_weather >> verify_pipeline >> stream_to_hadoop