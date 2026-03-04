from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from utils.airflow_utils import load_api_to_postgres


DEFAULT_ARGS = {
    "owner": "data-eng",
    "depends_on_past": False,
    "email_on_failure": True,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


with DAG(
    dag_id="rest_api_to_postgres",
    default_args=DEFAULT_ARGS,
    description="Extract REST API data and load into PostgreSQL",
    start_date=datetime(2026, 3, 1),
    catchup=False,
    max_active_runs=1,
    tags=["api", "postgres", "etl"],
    params={
        "api_url": "http://dummy-api-server:8000/nilai_csm",
        "target_conn_id": "bssn-dwh",
        "target_table": "public.nilai_csm",
    }
) as dag:

    api_load_to_pg_task = PythonOperator(
        task_id="load_api_to_postgres",
        python_callable=load_api_to_postgres,
    )


    api_load_to_pg_task
