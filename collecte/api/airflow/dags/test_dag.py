from datetime import datetime, timedelta
from airflow.decorators import task, dag

@dag(
    dag_id="first_dag",
    start_date=datetime(2025, 8, 5),
    schedule_interval=timedelta(minutes=2),
    catchup=False,
    tags=["first", "dag"]
)

def first_dag():
    @task
    def first_task():
        print("Hello first task")

    @task
    def second_task():
        print("Hello second task")

    first_task() >> second_task()

first_dag()