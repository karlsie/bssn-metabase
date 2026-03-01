from datetime import datetime, timedelta
import requests
import pandas as pd
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook


DEFAULT_ARGS = {
    "owner": "data-eng",
    "depends_on_past": False,
    "email_on_failure": True,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


API_URL = "http://localhost:8000/orders"
TABLE_NAME = "public.api_data"


headers = {
        "Content-Type": "application/json",
    }


# fetch data from api without pagination
def fetch_api_data():
    all_rows = []
    response = requests.get(API_URL, headers=headers, timeout=60)
    if response.status_code == 200:
        data = response.json()
        rows = data.get("results", [])
        all_rows.extend(rows)

    df = pd.json_normalize(all_rows)
    return df

def load_to_postgres(
        df,
        target_conn_id,
        target_table,
):
    if df:
        hook = PostgresHook(postgres_conn_id=target_conn_id)
        engine = hook.get_sqlalchemy_engine()

        df.to_sql(
            target_table.split(".")[-1],
            engine,
            schema=target_table.split(".")[0],
            if_exists="append",
            index=False,
            method="multi",
            chunksize=1000,
        )


def etl():
    df = fetch_api_data()
    load_to_postgres(df, target_conn_id="postgres_default", target_table=TABLE_NAME)


with DAG(
    dag_id="rest_api_to_postgres",
    default_args=DEFAULT_ARGS,
    description="Extract REST API data and load into PostgreSQL",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["api", "postgres", "etl"],
) as dag:

    api_load_to_pg_task = PythonOperator(
        task_id="api_load_to_pg_task",
        python_callable=etl,
    )


    api_load_to_pg_task
