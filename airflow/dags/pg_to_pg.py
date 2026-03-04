from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime
from utils.airflow_utils import transfer_postgres_to_postgres


with DAG(
    dag_id="postgres_to_postgres_transfer",
    start_date=datetime(2026, 3, 1),
    catchup=False,
    tags=["postgres", "etl"],
    params={  # Default values
        "source_conn_id": "bssn-dwh",
        "target_conn_id": "bssn-dwh",
        "source_table": "public.aset_tik",
        "target_table": "public.aset_tik_dt",
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
