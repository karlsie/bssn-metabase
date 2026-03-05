from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime, timedelta
from utils.airflow_utils import transfer_postgres_to_postgres
import json


DEFAULT_ARGS = {
    "owner": "data-eng",
    "depends_on_past": False,
    "email_on_failure": True,
    "retries": 0,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="pg_transfers_daily",
    start_date=datetime(2026, 3, 1),
    schedule="0 2 * * *",
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["postgres", "etl", "daily"],
) as dag:

    with open("/opt/airflow/dags/values/daily/pg_to_pg.json") as f:
        table_pairs = json.load(f)

    for pair in table_pairs:
        PythonOperator(
            task_id=f"transfer_{pair['src'].split('.')[-1]}",
            python_callable=transfer_postgres_to_postgres,
            op_kwargs={
                "source_conn_id": "pg-bssn-sources",
                "target_conn_id": "pg-bssn-dwh",
                "source_table": pair["src"],
                "target_table": pair["dst"],
                "load_type": pair["load_type"],
                "date_column": pair.get("date_column"),
                # "from_date": pair.get("from_date"),
                "from_date": "{{ macros.ds_add(ds, -1) }}"
            },
        )
