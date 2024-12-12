from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
}


with DAG(
    'example_postgres_dag',
    default_args=default_args,
    schedule_interval=None) as dag:
    
    create_table = PostgresOperator(
        task_id='create_table',
        postgres_conn_id='POSTGRES_CONNECTION',
        sql="""
        CREATE TABLE IF NOT EXISTS example_table (
            id SERIAL PRIMARY KEY,
            value TEXT NOT NULL
        );
        """
    )

    insert_data = PostgresOperator(
        task_id='insert_data',
        postgres_conn_id='POSTGRES_CONNECTION',
        sql="""
            INSERT INTO example_table (value) VALUES ('Hello, world!');
        """
    )

    create_table >> insert_data
