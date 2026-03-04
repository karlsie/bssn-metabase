import requests
import pandas as pd
from psycopg2 import sql
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
    conf = context["dag_run"].conf or {}

    source_conn_id = source_conn_id or conf.get("source_conn_id", context["params"]["source_conn_id"])
    target_conn_id = target_conn_id or conf.get("target_conn_id", context["params"]["target_conn_id"])
    source_table = source_table or conf.get("source_table", context["params"]["source_table"])
    target_table = target_table or conf.get("target_table", context["params"]["target_table"])

    load_type = load_type or conf.get("load_type", context["params"].get("load_type", "overwrite")).lower()
    date_column = date_column or conf.get("date_column", context["params"].get("date_column"))
    from_date = from_date or conf.get("from_date", context["params"].get("from_date"))

    if load_type not in ["overwrite", "append"]:
        raise ValueError("load_type must be either 'overwrite' or 'append'")

    if load_type == "append":
        if not date_column:
            raise ValueError("date_column is required when load_type='append'")
        if not from_date:
            raise ValueError("from_date is required when load_type='append'")

    source_hook = PostgresHook(postgres_conn_id=source_conn_id)
    target_hook = PostgresHook(postgres_conn_id=target_conn_id)

    source_conn = source_hook.get_conn()
    target_conn = target_hook.get_conn()

    source_cursor = source_conn.cursor()
    target_cursor = target_conn.cursor()

    try:
        if load_type == "overwrite":
            # Drop table if exists
            target_cursor.execute(
                sql.SQL("DROP TABLE IF EXISTS {}").format(sql.SQL(target_table))
            )

            # Recreate table from source
            target_cursor.execute(
                sql.SQL("CREATE TABLE {} AS SELECT * FROM {};").format(
                    sql.SQL(target_table),
                    sql.SQL(source_table),
                )
            )

            target_conn.commit()

        else:
            # Validate date column exists in source
            source_cursor.execute(
                """
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = %s
                AND column_name = %s
                """,
                (source_table.split(".")[-1], date_column),
            )

            if source_cursor.fetchone() is None:
                raise ValueError(
                    f"Column '{date_column}' does not exist in source table '{source_table}'"
                )

            insert_query = sql.SQL(
                """
                INSERT INTO {target}
                SELECT *
                FROM {source}
                WHERE {date_col} >= %s
                """
            ).format(
                target=sql.SQL(target_table),
                source=sql.SQL(source_table),
                date_col=sql.Identifier(date_column),
            )

            target_cursor.execute(insert_query, (from_date,))
            target_conn.commit()

    finally:
        source_cursor.close()
        target_cursor.close()
        source_conn.close()
        target_conn.close()


# fetch data from api without pagination
def load_api_to_postgres(api_url=None, target_conn_id=None, target_table=None, **context):
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

    if df.empty:
        print("No data to load")
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
