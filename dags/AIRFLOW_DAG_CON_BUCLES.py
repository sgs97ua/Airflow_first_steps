from datetime import datetime, timedelta
from airflow import DAG
from airflow.models import Variable
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.exceptions import AirflowException, AirflowSkipException, AirflowTaskTimeout
from airflow.utils.trigger_rule import TriggerRule
import time

ENV = Variable.get("env")
ID = Variable.get("id")
TAGS  = ["PythonDataFlow"]
DAG_ID = "AIRFLOW_DAG_CON_BUCLES"
DAG_DESCRIPTION = "DAG con bucles en Airflow"
DAG_SCHEDULE = "0 0 * * *"
default_args = {
    "start_date":datetime(2024,12,10),
}
retries = 0
retry_delay = timedelta(minutes=5)

params = {'Manual':True,
          'Fecha':datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

tablas_info = {
    1:{"message":"Soy la tarea 1"},
    2:{"message":"Soy la tarea 2"},
    3:{"message":"Soy la tarea 3"},
    4:{"message":"Soy la tarea 4"}
}

dag = DAG(
    DAG_ID,
    default_args=default_args,
    description=DAG_DESCRIPTION,
    catchup=False,
    schedule_interval=DAG_SCHEDULE,
    tags=TAGS,
    params=params
)

def create_task(message):
    def task_callable():
        print(message)
    return task_callable

with dag as dag:
    start_task = EmptyOperator(task_id="start")
    
    end_task = EmptyOperator(task_id="end")

    

    previous_task = start_task
    for tabla, info in tablas_info.items():
        message = info.get('message')
        python_task = PythonOperator(
            task_id=f"python_task{tabla}",
            python_callable= create_task(message)
        )

        previous_task >> python_task
        previous_task = python_task
    
    python_task >> end_task