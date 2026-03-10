import requests
import pandas as pd
import psycopg2
from sqlalchemy import inspect
from airflow.providers.postgres.hooks.postgres import PostgresHook


def _perform_upsert(df, engine, schema, table_name, keys, batch_size=1000):
    """Perform upsert operation by deleting and inserting data based on keys.
    
    This function deletes rows from the target table where the key columns match
    the values in the DataFrame, then inserts all rows from the DataFrame.
    
    Args:
        df: pandas DataFrame containing the data to upsert
        engine: SQLAlchemy engine connected to the target database
        schema: Schema name in PostgreSQL
        table_name: Table name in PostgreSQL
        keys: List of column names to use as keys for matching/deleting
        batch_size: Number of rows to process in each batch (default: 1000)
    """
    if df.empty:
        return
    
    # Ensure keys is a list
    if isinstance(keys, str):
        keys = [keys]
    
    # Get connection from engine
    with engine.connect() as connection:
        dbapi_conn = connection.connection
        
        try:
            cursor = dbapi_conn.cursor()
            
            # Process data in batches
            for i in range(0, len(df), batch_size):
                batch_df = df.iloc[i:i + batch_size].copy()
                
                # Delete existing rows based on keys
                delete_conditions = " AND ".join([f"{key} = %s" for key in keys])
                delete_query = f"DELETE FROM {schema}.{table_name} WHERE ({delete_conditions})"
                
                # Extract unique key combinations and delete
                for _, row in batch_df.iterrows():
                    key_values = tuple(row[key] for key in keys)
                    try:
                        cursor.execute(delete_query, key_values)
                    except psycopg2.Error as e:
                        dbapi_conn.rollback()
                        raise Exception(f"Error deleting from {schema}.{table_name}: {str(e)}")
                
                # Insert new rows
                columns = list(batch_df.columns)
                columns_str = ", ".join(columns)
                placeholders = ", ".join(["%s"] * len(columns))
                insert_query = f"INSERT INTO {schema}.{table_name} ({columns_str}) VALUES ({placeholders})"
                
                # Prepare data for insertion
                insert_data = [tuple(row[col] for col in columns) for _, row in batch_df.iterrows()]
                
                try:
                    cursor.executemany(insert_query, insert_data)
                    dbapi_conn.commit()
                except psycopg2.Error as e:
                    dbapi_conn.rollback()
                    raise Exception(f"Error inserting into {schema}.{table_name}: {str(e)}")
            
            cursor.close()
            
        except Exception as e:
            dbapi_conn.rollback()
            raise
        finally:
            dbapi_conn.close()


def transfer_postgres_to_postgres(
    source_conn_id=None,
    target_conn_id=None,
    source_table=None,
    target_table=None,
    load_type=None,
    date_column=None,
    from_date=None,
    keys=None,
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
    keys = keys or conf.get("keys", context["params"].get("keys"))

    if load_type == "upsert" and not keys:
        raise ValueError("Keys are required when load_type='upsert'")

    # Get SQLAlchemy engines
    source_hook = PostgresHook(postgres_conn_id=source_conn_id)
    target_hook = PostgresHook(postgres_conn_id=target_conn_id)
    source_engine = source_hook.get_sqlalchemy_engine()
    target_engine = target_hook.get_sqlalchemy_engine()

    # Build source query
    if date_column and from_date:
        source_query = f"SELECT * FROM {source_table} WHERE {date_column} >= '{from_date}'"
    else:
        source_query = f"SELECT * FROM {source_table}"

    # Read data into DataFrame
    df = pd.read_sql(source_query, source_engine)
    df.columns = df.columns.str.lower().str.replace(r'[^a-zA-Z0-9_]', '_', regex=True)
    df["updated_at"] = pd.Timestamp.now()

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
        if load_type == "overwrite":
            # If table exists and load_type is overwrite, replace it
            df.to_sql(target_table_name, target_engine, schema=target_schema, index=False, if_exists='replace', method='multi', chunksize=1000)
            print(f"Overwritten existing table {target_table} with {len(df)} rows.")
        elif load_type == "upsert":
            # Handle upsert logic
            _perform_upsert(df, target_engine, target_schema, target_table_name, keys)
            print(f"Upserted {len(df)} rows to existing table {target_table}.")
        else:
            raise ValueError("load_type must be 'overwrite' or 'upsert'")


def load_api_to_postgres(
        api_url=None,
        target_conn_id=None,
        target_table=None,
        load_type="append",
        keys=None,
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
    load_type = (load_type or conf.get("load_type", context["params"].get("load_type", "overwrite"))).lower()
    keys = keys or conf.get("keys", context["params"].get("keys"))

    if load_type == "upsert" and not keys:
        raise ValueError("Keys are required when load_type='upsert'")

    headers = {"Content-Type": "application/json"}

    response = requests.get(api_url, headers=headers, timeout=60)
    response.raise_for_status()

    data = response.json()
    rows = data.get("results", [])
    df = pd.json_normalize(rows)
    df.columns = df.columns.str.lower().str.replace(r'[^a-zA-Z0-9_]', '_', regex=True)
    df["updated_at"] = pd.Timestamp.now()

    if df.empty:
        print("No data to load")
        return

    schema, table = target_table.split(".")

    hook = PostgresHook(postgres_conn_id=target_conn_id)
    engine = hook.get_sqlalchemy_engine()

    # Check if target table exists
    inspector = inspect(engine)
    table_exists = table in inspector.get_table_names()

    if not table_exists:
        # If table doesn't exist, create it
        df.to_sql(table, engine, schema=schema, index=False, if_exists='fail', method='multi', chunksize=1000)
        print(f"Created target table {target_table} and inserted {len(df)} rows.")
    else:
        if load_type == "overwrite":
            df.to_sql(table, engine, schema=schema, index=False, if_exists='replace', method='multi', chunksize=1000)
            print(f"Overwritten existing table {target_table} with {len(df)} rows.")
        elif load_type == "upsert":
            # Handle upsert logic
            _perform_upsert(df, engine, schema, table, keys)
            print(f"Upserted {len(df)} rows to existing table {target_table}.")
        else:
            raise ValueError("load_type must be 'overwrite' or 'upsert'")


def query_dwh_to_dwh(
    target_conn_id=None,
    query_path=None,
    target_table=None,
    load_type=None,
    keys=None,
    **context
):
    """Running a query against a PostgreSQL database and loading the results into table in the same PostgreSQL database.

    Arguments may be provided via op_kwargs, dag params, or dag_run.conf.
    """

    conf = context["dag_run"].conf or {}

    target_conn_id = target_conn_id or conf.get("target_conn_id", context["params"].get("target_conn_id"))
    query_path = query_path or conf.get("query_path", context["params"].get("query_path"))
    target_table = target_table or conf.get("target_table", context["params"].get("target_table"))
    load_type = (load_type or conf.get("load_type", context["params"].get("load_type", "overwrite"))).lower()
    keys = keys or conf.get("keys", context["params"].get("keys"))

    if load_type == "upsert" and not keys:
        raise ValueError("Keys are required when load_type='upsert'")

    hook = PostgresHook(postgres_conn_id=target_conn_id)
    engine = hook.get_sqlalchemy_engine()

    with open(f"/opt/airflow/dags/sql/{query_path}") as sql_file:
        query = sql_file.read()
    df = pd.read_sql(query, engine)
    df.columns = df.columns.str.lower().str.replace(r'[^a-zA-Z0-9_]', '_', regex=True)
    df["updated_at"] = pd.Timestamp.now()

    if df.empty:
        print("No data to load")
        return

    schema, table = target_table.split(".")

    # Check if target table exists
    inspector = inspect(engine)
    table_exists = table in inspector.get_table_names()

    if not table_exists:
        # If table doesn't exist, create it
        df.to_sql(table, engine, schema=schema, index=False, if_exists='fail', method='multi', chunksize=1000)
        print(f"Created target table {target_table} and inserted {len(df)} rows.")
    else:
        if load_type == "overwrite":
            df.to_sql(table, engine, schema=schema, index=False, if_exists='replace', method='multi', chunksize=1000)
            print(f"Overwritten existing table {target_table} with {len(df)} rows.")
        elif load_type == "upsert":
            _perform_upsert(df, engine, schema, table, keys)
            print(f"Upserted {len(df)} rows to existing table {target_table}.")
        else:
            raise ValueError("load_type must be 'overwrite' or 'upsert'")
