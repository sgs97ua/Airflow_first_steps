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
DAG_ID = "MI_PRIMER_DAG"
DAG_DESCRIPTION = "Mi primer DAG en Airflow"
DAG_SCHEDULE = "0 0 * * *"
default_args = {
    "start_date":datetime(2024,12,10),
}
retries = 0
retry_delay = timedelta(minutes=5)

params = {'Manual':True,
          'Fecha':datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

def execute_tasks(**kwargs):
    params = kwargs.get('params',{})
    manual = params.get('Manual',False)

    if manual:
        raise AirflowException("La tarea ha fallado")

def second_tasks():
    print("Second_task")

dag = DAG(
    DAG_ID,
    default_args=default_args,
    description=DAG_DESCRIPTION,
    catchup=False,
    schedule_interval=DAG_SCHEDULE,
    max_active_runs=1,
    dagrun_timeout=timedelta(minutes=60),
    tags=TAGS,
    params=params
)

with dag as dag:
    start_task = EmptyOperator(task_id="inicia_proceso")
    
    end_task = EmptyOperator(task_id="finaliza_proceso",
                             trigger_rule=TriggerRule.NONE_FAILED,)

    first_task = PythonOperator(task_id="primer_proceso", 
                                python_callable=execute_tasks,
                                retries=retries,
                                retry_delay=retry_delay,
                                provide_context=True)
    
    second_task = PythonOperator(task_id="segundo_proceso",
                                  python_callable=second_tasks,
                                  provide_context=True)

    
    
    start_task >> [first_task,second_task] >> end_task