from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
}


def print_query_result(**kwargs):
    ti = kwargs['ti']
    query_results = ti.xcom_pull(task_ids='select_table')
    for row in query_results:
        print(row)


with DAG(
    'example_postgres_select_dag',
    default_args=default_args,
    schedule_interval=None,
    catchup=False) as dag:
    
    select_table = PostgresOperator(
        task_id='select_table',
        postgres_conn_id='POSTGRES_CONNECTION',
        sql="""
        SELECT * FROM example_table;
        """
    )

    print_results = PythonOperator(
        task_id='print_results',
        python_callable=print_query_result,

    )

    select_table >> print_results
