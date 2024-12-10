from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator

TAGS  = ["PythonDataFlow"]
DAG_ID = "MI_PRIMER_DAG"
DAG_DESCRIPTION = "Mi primer DAG en Airflow"
DAG_SCHEDULE = "0 0 * * *"
default_args = {
    "start_date":datetime(2024,12,10),
}
retries = 4
retry_delay = timedelta(minutes=5)

def execute_tasks():
    print("Hala Madrid")


dag = DAG(
    DAG_ID,
    default_args=default_args,
    description=DAG_DESCRIPTION,
    catchup=False,# Esto hace que el dag se ponga al día con todas las ejecuciones pendientes
    schedule_interval=DAG_SCHEDULE,
    max_active_runs=1,# Máxima número de ejecuciones que puede tener el dag
    dagrun_timeout=timedelta(minutes=60),
    tags=TAGS
)

with dag as dag:
    start_task = EmptyOperator(task_id="inicia_proceso")
    
    end_task = EmptyOperator(task_id="finaliza_proceso")

    first_task = PythonOperator(task_id="primer_proceso", 
                                python_callable=execute_tasks,
                                retries=retries,
                                retry_delay=retry_delay)
    
    start_task >> first_task >> end_task