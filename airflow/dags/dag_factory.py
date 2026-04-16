import json
import os
import logging
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
from airflow.models import Variable

# Import utils functions
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.notif_utils import construct_failure_message
from utils.airflow_utils import (
    transfer_postgres_to_postgres,
    query_dwh_to_dwh,
    load_api_to_postgres,
    load_only_office_file_to_postgres,
)

logger = logging.getLogger(__name__)

only_office_conn = Variable.get("only_office_conn", deserialize_json=True)


def send_failure_notification(context):
    """Send Slack notification on DAG failure."""

    message_dict = construct_failure_message(context)
    
    slack_alert = SlackWebhookOperator(
        task_id="slack_failure_notification",
        slack_webhook_conn_id="slack_api_default",
        message=message_dict["text"],
        blocks=message_dict["blocks"],
        channel="#pipeline-updates",
    )
    return slack_alert.execute(context=context)


class DagFactory:
    """Factory class for dynamically generating DAGs from JSON configuration files."""

    def __init__(self, values_dir="/opt/airflow/dags/jobs"):
        """Initialize DagFactory with the path to the jobs directory.

        Args:
            values_dir: Path to directory containing JSON configuration files
        """
        self.values_dir = values_dir

    def load_config(self, filename):
        """Load JSON configuration from file.

        Args:
            filename: Name of the JSON file to load

        Returns:
            Dictionary containing the configuration
        """
        filepath = os.path.join(self.values_dir, filename)
        with open(filepath, "r") as f:
            return json.load(f)

    def parse_default_args(self, config):
        """Parse and convert default_args from config to Airflow format.

        Args:
            config: Configuration dictionary from JSON

        Returns:
            Dictionary with parsed default_args for DAG
        """
        default_args = config.get("default_args", {})

        # Convert string values to appropriate types
        parsed_args = {
            "owner": default_args.get("owner", "airflow"),
            "depends_on_past": default_args.get("depends_on_past", False) == True,
            "email_on_failure": default_args.get("email_on_failure", False) == True,
            "retries": default_args.get("retries", 1),
            "retry_delay": timedelta(minutes=default_args.get("retry_delay", 5)),
            "on_failure_callback": send_failure_notification,
        }

        # Parse start_date
        if "start_date" in default_args:
            parsed_args["start_date"] = datetime.strptime(
                default_args["start_date"], "%Y-%m-%d"
            )

        return parsed_args

    def create_task_function(self, job_config):
        """Create a Python callable for a task based on job configuration.

        Args:
            job_config: Configuration dictionary for the job

        Returns:
            A callable function for the task
        """
        function_name = job_config.get("function")

        def task_func(**context):
            """Placeholder task function that imports and calls the appropriate function."""
            # Call task functions based on configuration
            if function_name == "pg_to_pg":
                return transfer_postgres_to_postgres(
                    source_table=job_config.get("src"),
                    source_conn_id=job_config.get("source_conn_id"),
                    target_table=job_config.get("dst"),
                    target_conn_id=job_config.get("target_conn_id"),
                    load_type=job_config.get("load_type", "overwrite"),
                    keys=job_config.get("keys"),
                    date_column=job_config.get("date_column"),
                    from_date=job_config.get("from_date"),
                    **context,
                )
            elif function_name == "dwh_to_dwh":
                return query_dwh_to_dwh(
                    query_path=job_config.get("query_path"),
                    target_table=job_config.get("dst"),
                    target_conn_id=job_config.get("target_conn_id"),
                    load_type=job_config.get("load_type", "overwrite"),
                    keys=job_config.get("keys"),
                    **context,
                )
            elif function_name == "rest_api_to_pg":
                return load_api_to_postgres(
                    api_url=job_config.get("api_url"),
                    target_table=job_config.get("dst"),
                    target_conn_id=job_config.get("target_conn_id"),
                    load_type=job_config.get("load_type", "overwrite"),
                    keys=job_config.get("keys"),
                    **context,
                )
            elif function_name == "only_office_to_pg":
                return load_only_office_file_to_postgres(
                    token=only_office_conn.get(job_config.get("only_office_conn")).get("token"),
                    password=only_office_conn.get(job_config.get("only_office_conn")).get("password"),
                    file_url=job_config.get("file_url"),
                    filename=job_config.get("filename"),
                    format=job_config.get("format"),
                    target_conn_id=job_config.get("target_conn_id"),
                    target_table=job_config.get("dst"),
                    load_type=job_config.get("load_type", "overwrite"),
                    keys=job_config.get("keys"),
                    **context,
                )
            else:
                raise ValueError(f"Unknown function: {function_name}")

        return task_func

    def generate_task_id(self, job_config):
        """Generate a meaningful task_id based on job configuration.

        Args:
            job_config: Configuration dictionary for the job

        Returns:
            Generated task_id string
        """
        # Check if task_id is explicitly provided
        if "task_id" in job_config:
            return job_config["task_id"]

        # Generate task_id based on destination or API endpoint
        dst = job_config.get("dst")
        function_name = job_config.get("function")

        return f"{function_name}_{dst.split('.')[-1]}"

    def generate_dag(self, config):
        """Generate a DAG from configuration dictionary.

        Args:
            config: Configuration dictionary from JSON file

        Returns:
            Generated DAG object
        """
        dag_id = config.get("dag_id")
        if not dag_id:
            raise ValueError("dag_id is required in configuration")

        default_args = self.parse_default_args(config)
        catchup = config.get("default_args", {}).get("catchup", False) == True
        tags = config.get("default_args", {}).get("tags", [])
        schedule = config.get("default_args", {}).get("schedule", None)

        logger.info(f"Creating DAG: {dag_id} with schedule: {schedule}")

        # Create DAG with both schedule_interval and schedule for compatibility
        dag_kwargs = {
            "dag_id": dag_id,
            "default_args": default_args,
            "schedule": schedule,  # New parameter name
            "catchup": catchup,
            "tags": tags,
        }

        dag = DAG(**dag_kwargs)

        # Create tasks from jobs
        jobs = config.get("jobs", [])
        if not jobs:
            logger.warning(f"No jobs defined for DAG: {dag_id}")
            return dag

        tasks = {}

        for idx, job_config in enumerate(jobs):
            task_id = self.generate_task_id(job_config)
            task_func = self.create_task_function(job_config)

            try:
                task = PythonOperator(
                    task_id=task_id,
                    python_callable=task_func,
                    dag=dag,
                )
                tasks[task_id] = task
                logger.info(f"Created task: {task_id} in DAG: {dag_id}")
            except Exception as e:
                logger.error(
                    f"Error creating task {task_id} in DAG {dag_id}: {str(e)}",
                    exc_info=True,
                )

        # Set up task dependencies
        for idx, job_config in enumerate(jobs):
            task_id = self.generate_task_id(job_config)
            depends_on = job_config.get("depends_on", [])

            # If depends_on is a list of table names, find all tasks that produce them
            if depends_on:
                for dep in depends_on:
                    dependency_found = False
                    # Search all jobs for the table producer, not only earlier jobs
                    for _, dep_job in enumerate(jobs):
                        if dep_job.get("dst") == dep:
                            dep_task_id = self.generate_task_id(dep_job)
                            if dep_task_id in tasks and task_id in tasks:
                                tasks[dep_task_id] >> tasks[task_id]
                                dependency_found = True
                                logger.info(
                                    f"Set dependency: {dep_task_id} >> {task_id}"
                                )
                    if not dependency_found:
                        logger.warning(
                            f"Dependency target '{dep}' for task '{task_id}' not found in jobs list."
                        )

        return dag

    def create_dags_from_directory(self):
        """Create all DAGs from JSON files in the values directory.

        Returns:
            Dictionary of generated DAGs with dag_id as key
        """
        dags = {}

        # Check if directory exists
        if not os.path.exists(self.values_dir):
            logger.error(f"Jobs directory does not exist: {self.values_dir}")
            return dags

        # Get all JSON files from values directory
        try:
            json_files = [f for f in os.listdir(self.values_dir) if f.endswith(".json")]
            logger.info(f"Found {len(json_files)} JSON files in {self.values_dir}")
        except Exception as e:
            logger.error(f"Error listing files in {self.values_dir}: {str(e)}")
            return dags

        for json_file in json_files:
            try:
                logger.info(f"Loading configuration from {json_file}")
                config = self.load_config(json_file)
                dag = self.generate_dag(config)
                dag_id = config.get("dag_id")
                dags[dag_id] = dag
                logger.info(f"Successfully generated DAG: {dag_id}")
            except FileNotFoundError as e:
                logger.error(f"File not found: {json_file} - {str(e)}")
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in {json_file}: {str(e)}")
            except Exception as e:
                logger.error(
                    f"Error generating DAG from {json_file}: {str(e)}", exc_info=True
                )

        logger.info(f"Generated {len(dags)} DAGs total")
        return dags


# Default factory instance
try:
    dag_factory = DagFactory()
    logger.info(f"DAG Factory initialized with directory: {dag_factory.values_dir}")

    # Generate all DAGs
    generated_dags = dag_factory.create_dags_from_directory()
    logger.info(f"Total DAGs generated: {len(generated_dags)}")

    # Make DAGs available to Airflow
    for dag_id, dag in generated_dags.items():
        globals()[dag_id] = dag
        logger.info(f"Registered DAG in globals: {dag_id}")

except Exception as e:
    logger.error(f"Failed to initialize DAG factory: {str(e)}", exc_info=True)
    generated_dags = {}
