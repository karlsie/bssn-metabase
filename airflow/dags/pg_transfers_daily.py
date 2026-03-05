from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime, timedelta
from utils.airflow_utils import transfer_postgres_to_postgres


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
    schedule="0 2 * * *",  # daily at 02:00 UTC
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["postgres", "etl", "daily"],
) as dag:

    table_pairs = [
        {"src": "public.aset_tik",      "dst": "public.aset_tik"},
        {"src": "public.aset_sistem",   "dst": "public.aset_sistem"},
        {"src": "public.kinerja_keamanan_siber",   "dst": "public.kinerja_keamanan_siber"},
        {"src": "public.nilai_indeks_kami",   "dst": "public.nilai_indeks_kami"},
        # add as many source/target pairs as you like
    ]

    for pair in table_pairs:
        PythonOperator(
            task_id=f"transfer_{pair['src'].split('.')[-1]}",
            python_callable=transfer_postgres_to_postgres,
            op_kwargs={               # passed via context to your util
                "source_conn_id": "pg-bssn-sources",
                "target_conn_id": "pg-bssn-dwh",
                "source_table": pair["src"],
                "target_table": pair["dst"],
                "load_type": "overwrite",        # override defaults if needed
                # "date_column": "created_at",
                # "from_date": "2026-03-01",
            },
        )
