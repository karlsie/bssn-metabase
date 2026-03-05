import requests
import pandas as pd
from sqlalchemy import inspect
from airflow.providers.postgres.hooks.postgres import PostgresHook


def transfer_postgres_to_postgres(
    source_conn_id=None,
    target_conn_id=None,
    source_table=None,
    target_table=None,
    load_type=None,
    date_column=None,
    from_date=None,
    **context
):
    """Fetch data from an postgreSQL database and load into another PostgreSQL database.

    Arguments may be provided via op_kwargs, dag params, or dag_run.conf.
    """

    conf = context["dag_run"].conf or {}

    source_conn_id = source_conn_id or conf.get("source_conn_id", context["params"]["source_conn_id"])
    target_conn_id = target_conn_id or conf.get("target_conn_id", context["params"]["target_conn_id"])
    source_table = source_table or conf.get("source_table", context["params"]["source_table"])
    target_table = target_table or conf.get("target_table", context["params"]["target_table"])
    load_type = (load_type or conf.get("load_type", context["params"].get("load_type", "overwrite"))).lower()
    date_column = date_column or conf.get("date_column", context["params"].get("date_column"))
    from_date = from_date or conf.get("from_date", context["params"].get("from_date"))

    if load_type not in ["overwrite", "append"]:
        raise ValueError("load_type must be 'overwrite' or 'append'")
    if load_type == "append" and (not date_column or not from_date):
        raise ValueError("date_column and from_date are required when load_type='append'")

    # Get SQLAlchemy engines
    source_hook = PostgresHook(postgres_conn_id=source_conn_id)
    target_hook = PostgresHook(postgres_conn_id=target_conn_id)
    source_engine = source_hook.get_sqlalchemy_engine()
    target_engine = target_hook.get_sqlalchemy_engine()

    # Build source query
    if load_type == "append":
        source_query = f"SELECT * FROM {source_table} WHERE {date_column} >= '{from_date}'"
    else:
        source_query = f"SELECT * FROM {source_table}"

    # Read data into DataFrame
    df = pd.read_sql(source_query, source_engine)

    # add column inserted_at current timestamp
    df["inserted_at"] = pd.Timestamp.now()
    if df.empty:
        print("No data to transfer.")
        return

    target_schema, target_table_name = target_table.split(".")

    # Check if target table exists
    inspector = inspect(target_engine)
    table_exists = target_table_name in inspector.get_table_names()


    if not table_exists:
        # If table doesn't exist, create it
        df.to_sql(target_table_name, target_engine, schema=target_schema, index=False, if_exists='fail', method='multi', chunksize=1000)
        print(f"Created target table {target_table} and inserted {len(df)} rows.")
    else:
        # If table exists, append
        df.to_sql(target_table_name, target_engine, schema=target_schema, index=False, if_exists='append', method='multi', chunksize=1000)
        print(f"Appended {len(df)} rows to existing table {target_table}.")


def load_api_to_postgres(
        api_url=None,
        target_conn_id=None,
        target_table=None,
        load_type="append",
        **context
):
    """Fetch data from an API and load into PostgreSQL.

    Arguments may be provided via op_kwargs, dag params, or dag_run.conf.
    """

    conf = context["dag_run"].conf or {}
    api_url = api_url or conf.get("api_url", context["params"].get("api_url"))
    target_conn_id = (
        target_conn_id
        or conf.get("target_conn_id", context["params"].get("target_conn_id"))
    )
    target_table = (
        target_table
        or conf.get("target_table", context["params"].get("target_table"))
    )

    headers = {"Content-Type": "application/json"}

    response = requests.get(api_url, headers=headers, timeout=60)
    response.raise_for_status()

    data = response.json()
    rows = data.get("results", [])
    df = pd.json_normalize(rows)
    df["inserted_at"] = pd.Timestamp.now()

    if df.empty:
        print("No data to load")
        return

    schema, table = target_table.split(".")

    hook = PostgresHook(postgres_conn_id=target_conn_id)
    engine = hook.get_sqlalchemy_engine()

    if load_type == "overwrite":
        df.to_sql(
            name=table,
            con=engine,
            schema=schema,
            if_exists="replace",  # drops and recreates table
            index=False,
            method="multi",
            chunksize=1000,
        )
    else:
        df.to_sql(
            name=table,
            con=engine,
            schema=schema,
            if_exists="append",  # creates if not exists, appends otherwise
            index=False,
            method="multi",
            chunksize=1000,
        )
