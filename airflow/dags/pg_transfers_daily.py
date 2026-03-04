from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime
from utils.airflow_utils import transfer_postgres_to_postgres


with DAG(
    dag_id="pg_transfers_daily",
    start_date=datetime(2026, 3, 1),
    schedule="0 2 * * *",  # daily at 02:00 UTC
    catchup=False,
    tags=["postgres", "etl"],
) as dag:

    table_pairs = [
        {"src": "public.aset_tik",      "dst": "public.aset_tik_dt"},
        {"src": "public.aset_sistem",   "dst": "public.aset_sistem_dt"},
        # add as many source/target pairs as you like
    ]

    for pair in table_pairs:
        PythonOperator(
            task_id=f"transfer_{pair['src'].split('.')[-1]}",
            python_callable=transfer_postgres_to_postgres,
            op_kwargs={               # passed via context to your util
                "source_table": pair["src"],
                "target_table": pair["dst"],
                "load_type": "append",        # override defaults if needed
                "date_column": "created_at",
                "from_date": "2026-03-01",
            },
        )
