from airflow import DAG
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.python import PythonOperator
from datetime import datetime


def transfer_postgres_to_postgres(
        source_conn_id,
        target_conn_id,
        source_table,
        target_table,
):
    source_hook = PostgresHook(postgres_conn_id=source_conn_id)
    target_hook = PostgresHook(postgres_conn_id=target_conn_id)

    source_conn = source_hook.get_conn()
    target_conn = target_hook.get_conn()

    source_cursor = source_conn.cursor()
    target_cursor = target_conn.cursor()

    try:
        # Example: Read from source
        source_cursor.execute(f"""
            SELECT *
            FROM {source_table}
        """)
        rows = source_cursor.fetchall()

        if rows:
            # Example: Write to target
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


with DAG(
    dag_id="postgres_to_postgres_transfer",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["postgres", "etl"],
) as dag:

    transfer_task = PythonOperator(
        task_id="transfer_data",
        python_callable=transfer_postgres_to_postgres,
        op_kwargs={
            "source_conn_id": "postgres_source",
            "target_conn_id": "postgres_target",
            "source_table": "users",
            "target_table": "users_copy"
        }
    )

    transfer_task
