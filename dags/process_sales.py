from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import requests
from dotenv import load_dotenv
import os

load_dotenv()
BASE_DIR = os.getenv('BASE_DIR')

DEFAULT_ARGS = {
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'max_active_runs': 1,
    'start_date': datetime(2022, 8, 9),
    'end_date': datetime(2022, 8, 12)
}


def extract_data_from_api(**kwargs):
    date = kwargs['date']
    raw_dir = BASE_DIR + f'/raw/sales/{date}'
    print(raw_dir)
    print(date)
    response = requests.post('http://localhost:8081/job_1', json={'raw_dir': raw_dir, 'date': date})
    if response.status_code != 201:
        raise Exception(response.status_code, 'Failed to get data from API')


def convert_to_avro(**kwargs):
    date = kwargs['date']
    raw_dir = BASE_DIR + f'/raw/sales/{date}'
    stg_dir = BASE_DIR + f'/stg/sales/{date}'
    response = requests.post('http://localhost:8082/job_2', json={'raw_dir': raw_dir, 'stg_dir': stg_dir})
    if response.status_code != 201:
        raise Exception(response.status_code, 'Failed to post to avro')


with DAG(
        dag_id='process_sales',
        schedule_interval='0 1 * * *',
        catchup=True,
        default_args=DEFAULT_ARGS,
        tags=['process_sales']
) as dag:
    task_1 = PythonOperator(
        task_id='extract_data_from_api',
        python_callable=extract_data_from_api,
        op_kwargs={'date': '{{ds}}'}
    )
    task_2 = PythonOperator(
        task_id='convert_to_avro',
        python_callable=convert_to_avro,
        op_kwargs={'date': '{{ds}}'}
    )

    task_1 >> task_2
