import requests
import pandas as pd
from airflow.providers.postgres.hooks.postgres import PostgresHook


def transfer_postgres_to_postgres(**context):
    # Runtime parameters (from manual trigger)
    conf = context["dag_run"].conf or {}

    source_conn_id = conf.get("source_conn_id", context["params"]["source_conn_id"])
    target_conn_id = conf.get("target_conn_id", context["params"]["target_conn_id"])
    source_table = conf.get("source_table", context["params"]["source_table"])
    target_table = conf.get("target_table", context["params"]["target_table"])

    source_hook = PostgresHook(postgres_conn_id=source_conn_id)
    target_hook = PostgresHook(postgres_conn_id=target_conn_id)

    source_conn = source_hook.get_conn()
    target_conn = target_hook.get_conn()

    source_cursor = source_conn.cursor()
    target_cursor = target_conn.cursor()

    try:
        source_cursor.execute(f"SELECT * FROM {source_table}")
        rows = source_cursor.fetchall()

        if rows:
            insert_query = f"""
                INSERT INTO {target_table}
                SELECT *
                FROM {source_table}
            """
            target_cursor.execute(insert_query)
            target_conn.commit()

    finally:
        source_cursor.close()
        target_cursor.close()
        source_conn.close()
        target_conn.close()


# fetch data from api without pagination
def load_api_to_postgres(**context):
    conf = context["dag_run"].conf or {}
    api_url = conf.get("api_url", context["params"]["api_url"])
    target_conn_id = conf.get("target_conn_id", context["params"]["target_conn_id"])
    target_table = conf.get("target_table", context["params"]["target_table"])

    headers = {"Content-Type": "application/json"}

    response = requests.get(api_url, headers=headers, timeout=60)
    response.raise_for_status()

    data = response.json()
    rows = data.get("results", [])
    df = pd.json_normalize(rows)

    if df.empty:
        return

    schema, table = target_table.split(".")

    hook = PostgresHook(postgres_conn_id=target_conn_id)
    engine = hook.get_sqlalchemy_engine()

    df.to_sql(
        name=table,
        con=engine,
        schema=schema,
        if_exists="append",  # creates if not exists, appends otherwise
        index=False,
        method="multi",
        chunksize=1000,
    )
