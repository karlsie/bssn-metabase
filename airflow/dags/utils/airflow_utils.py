from airflow.providers.postgres.hooks.postgres import PostgresHook
from utils.db_utils import read_postgredb, write_postgredb
from utils.api_utils import fetch_api_data
from utils.drive_utils import (
    download_file_from_only_office,
    read_file_from_only_office,
)


def transfer_postgres_to_postgres(
    source_conn_id=None,
    target_conn_id=None,
    source_table=None,
    target_table=None,
    load_type=None,
    date_column=None,
    from_date=None,
    keys=None,
    **context,
):
    """Fetch data from an postgreSQL database and load into another PostgreSQL database.

    Arguments may be provided via op_kwargs, dag params, or dag_run.conf.
    """

    conf = context["dag_run"].conf or {}

    source_conn_id = source_conn_id or conf.get(
        "source_conn_id", context["params"]["source_conn_id"]
    )
    target_conn_id = target_conn_id or conf.get(
        "target_conn_id", context["params"]["target_conn_id"]
    )
    source_table = source_table or conf.get(
        "source_table", context["params"]["source_table"]
    )
    target_table = target_table or conf.get(
        "target_table", context["params"]["target_table"]
    )
    load_type = (
        load_type
        or conf.get("load_type", context["params"].get("load_type", "overwrite"))
    ).lower()
    date_column = date_column or conf.get(
        "date_column", context["params"].get("date_column")
    )
    from_date = from_date or conf.get("from_date", context["params"].get("from_date"))
    keys = keys or conf.get("keys", context["params"].get("keys"))

    # Get SQLAlchemy engines
    source_hook = PostgresHook(postgres_conn_id=source_conn_id)
    target_hook = PostgresHook(postgres_conn_id=target_conn_id)
    source_engine = source_hook.get_sqlalchemy_engine()
    target_engine = target_hook.get_sqlalchemy_engine()

    df = read_postgredb(
        engine=source_engine,
        table_name=source_table,
        date_column=date_column,
        from_date=from_date,
    )

    write_postgredb(df, target_engine, target_table, load_type=load_type, keys=keys)


def load_api_to_postgres(
    api_url=None,
    target_conn_id=None,
    target_table=None,
    load_type="append",
    keys=None,
    **context,
):
    """Fetch data from an API and load into PostgreSQL.

    Arguments may be provided via op_kwargs, dag params, or dag_run.conf.
    """

    conf = context["dag_run"].conf or {}
    api_url = api_url or conf.get("api_url", context["params"].get("api_url"))
    target_conn_id = target_conn_id or conf.get(
        "target_conn_id", context["params"].get("target_conn_id")
    )
    target_table = target_table or conf.get(
        "target_table", context["params"].get("target_table")
    )
    load_type = (
        load_type
        or conf.get("load_type", context["params"].get("load_type", "overwrite"))
    ).lower()
    keys = keys or conf.get("keys", context["params"].get("keys"))

    headers = {"Content-Type": "application/json"}
    df = fetch_api_data(api_url, headers=headers)

    hook = PostgresHook(postgres_conn_id=target_conn_id)
    engine = hook.get_sqlalchemy_engine()
    write_postgredb(df, engine, target_table, load_type=load_type, keys=keys)


def query_dwh_to_dwh(
    target_conn_id=None,
    query_path=None,
    target_table=None,
    load_type=None,
    keys=None,
    **context,
):
    """Running a query against a PostgreSQL database and loading the results into table in the same PostgreSQL database.

    Arguments may be provided via op_kwargs, dag params, or dag_run.conf.
    """

    conf = context["dag_run"].conf or {}

    target_conn_id = target_conn_id or conf.get(
        "target_conn_id", context["params"].get("target_conn_id")
    )
    query_path = query_path or conf.get(
        "query_path", context["params"].get("query_path")
    )
    target_table = target_table or conf.get(
        "target_table", context["params"].get("target_table")
    )
    load_type = (
        load_type
        or conf.get("load_type", context["params"].get("load_type", "overwrite"))
    ).lower()
    keys = keys or conf.get("keys", context["params"].get("keys"))

    hook = PostgresHook(postgres_conn_id=target_conn_id)
    engine = hook.get_sqlalchemy_engine()

    df = read_postgredb(
        engine=engine,
        query_path=query_path,
    )

    write_postgredb(df, engine, target_table, load_type=load_type, keys=keys)


def load_only_office_file_to_postgres(
    # conn_username,
    # conn_password,
    token,
    password,
    file_url,
    format,
    filename,
    target_conn_id,
    target_table,
    load_type=None,
    keys=None,
    **context,
):
    """Fetch files from OnlyOffice, read the content, and load into PostgreSQL."""

    conf = context["dag_run"].conf or {}
    # conn_username = conn_username or conf.get(
    #     "conn_username", context["params"].get("conn_username")
    # )
    # conn_password = conn_password or conf.get(
    #     "conn_password", context["params"].get("conn_password")
    # )
    token = token or conf.get("token", context["params"].get("token"))
    password = password or conf.get("password", context["params"].get("password"))
    file_url = file_url or conf.get(
        "file_url", context["params"].get("file_url")
    )
    filename = filename or conf.get(
        "filename", context["params"].get("filename")
    )
    format = format or conf.get(
        "format", context["params"].get("format")
    )
    target_conn_id = target_conn_id or conf.get(
        "target_conn_id", context["params"].get("target_conn_id")
    )
    target_table = target_table or conf.get(
        "target_table", context["params"].get("target_table")
    )
    load_type = (
        load_type
        or conf.get("load_type", context["params"].get("load_type", "overwrite"))
    ).lower()
    keys = keys or conf.get("keys", context["params"].get("keys"))

    print(f"Processing file: {filename}")
    download_file_from_only_office(file_url, filename, token, password)

    content = read_file_from_only_office(f"/tmp/{filename}", format)

    hook = PostgresHook(postgres_conn_id=target_conn_id)
    engine = hook.get_sqlalchemy_engine()
    write_postgredb(
        content, engine, target_table, load_type=load_type, keys=keys
    )
