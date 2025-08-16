from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

# ==== CONFIGURATION DE BASE ====
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=3),
}

# ==== CRÉATION DU DAG ====
with DAG(
    dag_id='send_weather_to_kafka',
    default_args=default_args,
    description='Récupère les données météo et les envoie vers Kafka toutes les heures',
    schedule_interval=timedelta(hours=2),  # Exécution chaque heure
    start_date=datetime(2025, 8, 6),
    catchup=False,
    tags=['weather', 'kafka'],
) as dag:

    # ==== TÂCHE 1 : Lancer le producer météo ====
    fetch_and_send_weather = BashOperator(
        task_id='fetch_and_send_weather',
        bash_command='cd /opt/airflow/scripts && python3 kafka/producer.py'
    )

    # ==== TÂCHE 2 : Lancer le consumer vers Redis ====
    verify_pipeline = BashOperator(
        task_id='verify_pipeline',
        bash_command='''
            echo " Attente traitement Logstash..." && sleep 30 &&
            curl -s "http://elasticsearch:9200/_cat/indices/weather*" || echo "Pas encore d'index weather"
        ''',
        trigger_rule='all_done'  # S'exécute même si producer échoue
    )
    
    # ==== DÉPENDANCES ====
    fetch_and_send_weather >> verify_pipeline