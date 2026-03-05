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
    dag_id="rest_api_to_pg_daily",
    default_args=DEFAULT_ARGS,
    description="Extract REST API data and load into PostgreSQL",
    start_date=datetime(2026, 3, 1),
    schedule="0 2 * * *",  # daily at 02:00 UTC
    catchup=False,
    max_active_runs=1,
    tags=["api", "postgres", "etl", "daily"],
) as dag:

    # default list of api/target pairs; the number of tasks is fixed at parse time
    api_targets = [
        {"api_url": "http://dummy-api-server:8000/nilai_csm", "target_table": "public.nilai_csm"},
        # add additional entries here as needed
    ]

    # create a task for each configured pair
    for pair in api_targets:
        PythonOperator(
            task_id=f"load_api_{pair['target_table'].split('.')[-1]}",
            python_callable=load_api_to_postgres,
            op_kwargs={
                "api_url": pair["api_url"],
                # connection id can still be overridden at runtime via conf
                "target_conn_id": "pg-bssn-dwh",
                "target_table": pair["target_table"],
            },
        )
