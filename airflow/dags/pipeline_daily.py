from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime, timedelta
from utils.airflow_utils import (
    transfer_postgres_to_postgres,
    query_dwh_to_dwh,
    load_api_to_postgres,
)
import json


DEFAULT_ARGS = {
    "owner": "bssn-dwh",
    "depends_on_past": False,
    "email_on_failure": True,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


with DAG(
    dag_id="pipeline_daily",
    start_date=datetime(2026, 3, 1),
    schedule="0 2 * * *",
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["postgres", "etl", "daily"],
) as dag:

    with open("/opt/airflow/dags/values/daily.json") as f:
        table_pairs = json.load(f)

    tasks = {}
    for pair in table_pairs:
        if pair.get("function") == "transfer_postgres_to_postgres":
            task = PythonOperator(
                task_id=f"transfer_{pair['dst'].split('.')[-1]}",
                python_callable=transfer_postgres_to_postgres,
                op_kwargs={
                    "source_conn_id": "pg-bssn-sources",
                    "target_conn_id": "pg-bssn-dwh",
                    "source_table": pair["src"],
                    "target_table": pair["dst"],
                    "load_type": pair["load_type"],
                    "date_column": pair.get("date_column"),
                    # "from_date": "{{ macros.ds_add(ds, -1) }}",
                    "from_date": "2026-01-01",
                    "keys": pair.get("keys")
                },
            )
        elif pair.get("function") == "dwh_to_dwh":
            task = PythonOperator(
                task_id=f"transfer_{pair['dst'].split('.')[-1]}",
                python_callable=query_dwh_to_dwh,
                op_kwargs={
                    "target_conn_id": "pg-bssn-dwh",
                    "query_path": pair["query_path"],
                    "target_table": pair["dst"],
                    "load_type": pair["load_type"],
                    "keys": pair.get("keys")
                },
            )
        elif pair.get("function") == "rest_api_to_postgres":
            task = PythonOperator(
                task_id=f"load_api_{pair['dst'].split('.')[-1]}",
                python_callable=load_api_to_postgres,
                op_kwargs={
                    "api_url": pair["api_url"],
                    # connection id can still be overridden at runtime via conf
                    "target_conn_id": "pg-bssn-dwh",
                    "target_table": pair["dst"],
                    "load_type": pair["load_type"],
                    "keys": pair.get("keys")
                },
            )
        tasks[pair["dst"]] = task

    # Set dependencies from config
    for pair in table_pairs:
        if 'depends_on' in pair:
            depends_on = pair['depends_on']
            
            # Handle both single string and list of strings
            if isinstance(depends_on, str):
                depends_on = [depends_on]
            
            # Get current task
            current_task_key = pair["dst"]
            current_task = tasks.get(current_task_key)
            
            # Set all upstream tasks
            if current_task:
                for dep in depends_on:
                    if dep in tasks:
                        tasks[dep] >> current_task
