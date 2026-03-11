import psycopg2
import pandas as pd
from sqlalchemy import inspect


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
                batch_df = df.iloc[i : i + batch_size].copy()

                # Delete existing rows based on keys
                delete_conditions = " AND ".join([f"{key} = %s" for key in keys])
                delete_query = (
                    f"DELETE FROM {schema}.{table_name} WHERE ({delete_conditions})"
                )

                # Extract unique key combinations and delete
                for _, row in batch_df.iterrows():
                    key_values = tuple(row[key] for key in keys)
                    try:
                        cursor.execute(delete_query, key_values)
                    except psycopg2.Error as e:
                        dbapi_conn.rollback()
                        raise Exception(
                            f"Error deleting from {schema}.{table_name}: {str(e)}"
                        )

                # Insert new rows
                columns = list(batch_df.columns)
                columns_str = ", ".join(columns)
                placeholders = ", ".join(["%s"] * len(columns))
                insert_query = f"INSERT INTO {schema}.{table_name} ({columns_str}) VALUES ({placeholders})"

                # Prepare data for insertion
                insert_data = [
                    tuple(row[col] for col in columns) for _, row in batch_df.iterrows()
                ]

                try:
                    cursor.executemany(insert_query, insert_data)
                    dbapi_conn.commit()
                except psycopg2.Error as e:
                    dbapi_conn.rollback()
                    raise Exception(
                        f"Error inserting into {schema}.{table_name}: {str(e)}"
                    )

            cursor.close()

        except Exception as e:
            dbapi_conn.rollback()
            raise
        finally:
            dbapi_conn.close()


def read_postgredb(
    engine,
    table_name=None,
    query_path=None,
    date_column=None,
    from_date=None,
):
    """Read data from PostgreSQL database into a pandas DataFrame.

    Args:
        engine: SQLAlchemy engine for the PostgreSQL database
        date_column: Optional column name to filter by date
        from_date: Optional date value to filter the date_column (format: 'YYYY-MM-DD')
    Returns:
        A pandas DataFrame containing the data read from the database
    """

    if table_name and not query_path:
        # Get column names from the table
        _, target_table_name = table_name.split(".")
        inspector = inspect(engine)
        table_columns = inspector.get_columns(target_table_name)
        column_names = [col["name"] for col in table_columns]

        if date_column and date_column not in column_names:
            raise ValueError(
                f"Date column '{date_column}' does not exist in table '{table_name}'"
            )

        # Build source query
        if date_column and from_date:
            query = f"SELECT * FROM {table_name} WHERE {date_column} >= '{from_date}'"
        else:
            query = f"SELECT * FROM {table_name}"
    elif query_path and not table_name:
        QUERY_PATH = f"/opt/airflow/dags/sql/{query_path}"
        with open(QUERY_PATH, "r") as file:
            query = file.read()
    else:
        raise ValueError(
            "Either table_name or query_path must be provided, but not both."
        )

    # Read data into DataFrame
    df = pd.read_sql(query, engine)
    df.columns = df.columns.str.lower().str.replace(r"[^a-zA-Z0-9_]", "_", regex=True)
    df["updated_at"] = pd.Timestamp.now()

    return df


def write_postgredb(df, engine, target_table, load_type, keys=None):
    """Write a pandas DataFrame to a PostgreSQL database.

    Args:
        df: pandas DataFrame containing the data to write
        engine: SQLAlchemy engine for the target PostgreSQL database
        target_table: Target table name in the format 'schema.table'
        load_type: Type of load operation ('overwrite' or 'upsert')
        keys: List of column names to use as keys for upsert (required if load_type='upsert')
    """

    if df.empty:
        print("No data to load")
        return

    if load_type == "upsert" and not keys:
        raise ValueError("Keys are required when load_type='upsert'")

    target_schema, target_table_name = target_table.split(".")
    inspector = inspect(engine)
    table_exists = target_table_name in inspector.get_table_names()

    if not table_exists:
        # If table doesn't exist, create it by writing the DataFrame (this will create the table with appropriate schema)
        df.to_sql(
            target_table_name,
            engine,
            schema=target_schema,
            index=False,
            if_exists="fail",
            method="multi",
            chunksize=1000,
        )
        print(f"Created target table {target_table} and inserted {len(df)} rows.")
    else:
        if load_type == "overwrite":
            # If table exists and load_type is overwrite, replace it
            df.to_sql(
                target_table_name,
                engine,
                schema=target_schema,
                index=False,
                if_exists="replace",
                method="multi",
                chunksize=1000,
            )
            print(f"Overwritten existing table {target_table} with {len(df)} rows.")
        elif load_type == "upsert":
            # Perform upsert by deleting matching rows and inserting new data
            _perform_upsert(df, engine, target_schema, target_table_name, keys)
            print(f"Upserted {len(df)} rows to existing table {target_table}.")
        else:
            raise ValueError("load_type must be 'overwrite' or 'upsert'")
