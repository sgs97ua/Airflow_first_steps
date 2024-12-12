from airflow import DAG
from airflow.decorators import task
from airflow.operators.empty import EmptyOperator
from datetime import datetime, timedelta
from airflow.providers.http.operators.http import SimpleHttpOperator


dag_owner = "airflow"

defalut_args = {
    "owner": dag_owner,
    "depends_on_past": False,
    "retries": 2,
    "retry_delay":timedelta(minutes=5),
}


with DAG(
    dag_id='DAG_EXAMPLE_HTTP',
    description='Ejemplo de consumición de API con HTTP',
) as dag:
    

    start = EmptyOperator(task_id="start")


    http = SimpleHttpOperator(
        task_id="http_petition",
        method="GET",
        http_conn_id="JsonPlaceHolder",
        endpoint="posts",
        log_response=True,
        headers={"Content-Type": "application/json"},
        data={"id":"4"}
        
    )
    end = EmptyOperator(task_id="end")

    start >> http >> end