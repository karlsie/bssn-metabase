from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime
from utils.airflow_utils import transfer_postgres_to_postgres

DEFAULT_ARGS = {
    "owner": "bssn-dwh",
}


with DAG(
    dag_id="manual_pg_to_pg_transfer",
    start_date=datetime(2026, 3, 1),
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["manual","postgres", "etl"],
    params={  # Default values
        "source_conn_id": "pg-bssn-sources",
        "target_conn_id": "pg-bssn-dwh",
        "source_table": "public.aset_tik",
        "target_table": "public.aset_tik",
        "load_type": "append",  # or "overwrite"
        "date_column": "created_at",
        "from_date": "2026-03-01",
    },
) as dag:
    
    transfer_task = PythonOperator(
        task_id="transfer_data",
        python_callable=transfer_postgres_to_postgres,
    )


    transfer_task
