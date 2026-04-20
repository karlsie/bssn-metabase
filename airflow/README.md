# Airflow

Apache Airflow setup for BSSN Metabase data orchestration and ETL pipelines.

## Overview

This Airflow instance manages automated data pipelines for:
- **PostgreSQL to PostgreSQL data transfers** with support for full and incremental loads
- **REST API data ingestion** into PostgreSQL databases
- **ETL workflows** for the BSSN cybersecurity monitoring system

## Directory Structure

```
airflow/
├── config/
│   └── airflow.cfg                     # Airflow configuration file
├── dags/
│   ├── dag_factory.py                  # Dynamic DAG factory that generates DAGs from JSON
│   ├── jobs/                           # JSON configuration files for DAGs
│   │   ├── daily.json                  # Daily pipeline definition
│   │   ├── weekly.json                 # Weekly pipeline definition
│   │   └── monthly.json                # Monthly pipeline definition
│   ├── sql/                            # SQL query files for ETL
│   │   └── joined_data.sql             # SQL for data transformations
│   └── utils/
│       ├── __init__.py
│       ├── airflow_utils.py            # Task execution functions
│       ├── api_utils.py                # REST API data fetching utilities (returns pandas DataFrames)
│       ├── db_utils.py                 # Database connection and query utilities
│       ├── drive_utils.py              # OnlyOffice file download and parsing
│       └── notif_utils.py              # Slack notification utilities
├── logs/                                # DAG execution logs (auto-generated)
├── plugins/                             # Custom plugins directory
├── docker-compose.yaml                  # Docker Compose configuration
├── Dockerfile                           # Custom Airflow image (if needed)
├── Makefile                             # Common commands
├── requirements.txt                     # Python dependencies
└── README.md                            # This file
```

## Available DAGs

DAGs are **dynamically generated** from JSON configuration files in the `dags/jobs/` directory using the `DagFactory` class.

### Dynamic DAG Generation

The `dag_factory.py` file automatically:
1. Reads JSON configuration files from `dags/jobs/`
2. Validates configurations
3. Creates DAGs with tasks and dependencies
4. Registers them with Airflow

No manual DAG file creation needed—just add/modify JSON files!

### Available DAGs

- **`pipeline_daily`** – Runs every day at 02:00 UTC
  - Loads cybersecurity metrics from multiple sources
  - Performs data validation and transformation
  - Configured in `dags/jobs/daily.json`
  - Tasks: `kinerja_keamanan_siber`, `nilai_indeks_kami`, `joined_data`, `nilai_csm`, `only_office_data`

- **`pipeline_weekly`** – Runs weekly on Mondays at 02:00 UTC
  - Aggregates weekly asset and system metrics
  - Configured in `dags/jobs/weekly.json`

- **`pipeline_monthly`** – Runs monthly on day 1 at 02:00 UTC
  - Performs monthly reconciliation and reporting
  - Configured in `dags/jobs/monthly.json`

### Task Types

DAGs support three types of tasks:

1. **`transfer_postgres_to_postgres`** – PostgreSQL to PostgreSQL transfers
   - Supports `upsert`, `overwrite`, and `append` load types
   - Deletes existing rows matching key columns, then inserts new data (for upsert)

2. **`dwh_to_dwh`** – Query-based transformations
   - Executes SQL from `dags/sql/` directory
   - Supports complex ETL transformations

3. **`rest_api_to_postgres`** – REST API ingestion
   - Fetches JSON data from APIs
   - Loads into PostgreSQL tables

4. **`only_office_to_pg`** – OnlyOffice file ingestion
   - Downloads files from OnlyOffice servers
   - Parses CSV/XLSX/XLS files and loads into PostgreSQL

### Task ID Configuration

Task IDs must be explicitly specified in the job configuration using the `task_id` field. The factory no longer generates task IDs automatically.

### JSON Configuration Format

```json
{
    "dag_id": "pipeline_daily",
    "default_args": {
        "owner": "bssn-dwh",
        "depends_on_past": false,
        "email_on_failure": true,
        "retries": 2,
        "retry_delay": 5,
        "start_date": "2026-03-01",
        "schedule": "0 2 * * *",
        "catchup": false,
        "tags": ["postgres", "etl", "daily"]
    },
    "jobs": [
        {
            "task_id": "pg_to_pg_kinerja_keamanan_siber_dst",
            "function": "pg_to_pg",
            "source_conn_id": "pg-bssn-sources",
            "target_conn_id": "pg-bssn-dwh",
            "src": "public.kinerja_keamanan_siber",
            "dst": "public.kinerja_keamanan_siber_dst",
            "load_type": "upsert",
            "keys": ["id_stakeholder"]
        },
        {
            "task_id": "dwh_to_dwh_joined_data_dst",
            "function": "dwh_to_dwh",
            "query_path": "joined_data.sql",
            "target_conn_id": "pg-bssn-dwh",
            "dst": "public.joined_data_dst",
            "depends_on": ["pg_to_pg_kinerja_keamanan_siber_dst"],
            "load_type": "upsert",
            "keys": ["id_stakeholder"]
        }
    ]
}
```

## Setup

### Prerequisites

- Docker & Docker Compose
- Make (optional, for convenience commands)

### Installation

1. **Initialize Airflow database and user in DEV:**
   ```bash
   make dev
   ```
   This runs on `.env.dev` configuration. It performs the following steps:
   - `docker-compose --env-file .env.dev up -d airflow-init` - Initializes the database
   - `docker-compose --env-file .env.dev --profile flower up -d` - Starts all services including Flower monitoring

2. **Initialize Airflow database and user in PROD:**
   ```bash
   make prod
   ```
   This uses `.env` file for production configuration. It performs the following steps:
   - `docker-compose --env-file .env up -d airflow-init` - Initializes the database
   - `docker-compose --env-file .env --profile flower up -d` - Starts all services including Flower monitoring

3. **Check service status:**
   ```bash
   make status
   ```

4. **Access Airflow UI:**
   - URL: based on Airflow Variable `airflow_url`
   - Default credentials: `airflow` / `airflow`

### Shutdown

```bash
make down
```

Removes all containers, volumes, and images.

## Configuration

### Environment Variables

Configure in `.env` file or modify `docker-compose.yaml`:

- `AIRFLOW_IMAGE_NAME` - Docker image name (default: `apache/airflow:3.1.5`)
- `AIRFLOW_UID` - User ID in containers (default: `50000`)
- `AIRFLOW_PROJ_DIR` - Base directory for volumes (default: `.`)
- `_AIRFLOW_WWW_USER_USERNAME`
- `_AIRFLOW_WWW_USER_PASSWORD`

### PostgreSQL Connections

Configure database connections in Airflow UI:
1. Admin → Connections → Create New Connection
2. Set up `bssn-dwh` connection with your PostgreSQL credentials

Example:
- **Connection ID:** `bssn-dwh`
- **Connection Type:** Postgres
- **Host:** PostgreSQL server hostname
- **Port:** 5432
- **Database:** Your database name
- **Login/Password:** Database credentials

## Dependencies

Installed packages:
- `apache-airflow-providers-postgres` - PostgreSQL provider for Airflow
- `psycopg2-binary` - PostgreSQL Python adapter
- `requests` - HTTP client for REST API calls
- `pandas` - Data manipulation and analysis
- `sqlalchemy` - SQL toolkit and ORM

## Utilities

### `airflow_utils.py`

Contains task execution functions:

- **`transfer_postgres_to_postgres(**context)`**
  - Transfers data between PostgreSQL tables
  - Supports `upsert` (delete + insert on key match) and `overwrite` modes
  - Validates schema and date columns
  - Parameters: `source_conn_id`, `target_conn_id`, `source_table`, `target_table`, `load_type`, `keys`, `date_column`, `from_date`

- **`query_dwh_to_dwh(**context)`**
  - Executes SQL queries from files for transformations
  - Loads results into target tables
  - Parameters: `target_conn_id`, `query_path`, `target_table`, `load_type`, `keys`

- **`load_api_to_postgres(**context)`**
  - Fetches JSON data from REST APIs
  - Automatically cleans column names (replaces special chars with underscore)
  - Loads into PostgreSQL tables
  - Parameters: `api_url`, `target_conn_id`, `target_table`, `load_type`, `keys`

### `db_utils.py`

Database utility functions:

- **`_perform_upsert(df, engine, schema, table_name, keys, batch_size)`**
  - Deletes existing rows matching key columns
  - Inserts new rows from DataFrame
  - Processes in batches for memory efficiency
  - Uses psycopg2 for direct database operations

- **`read_postgredb(engine, table_name, query_path, date_column, from_date)`**
  - Reads data from PostgreSQL tables or SQL files
  - Validates date columns exist
  - Returns DataFrame with cleaned column names

- **`write_postgredb(df, engine, target_table, load_type, keys)`**
  - Writes DataFrame to PostgreSQL
  - Handles table creation if not exists
  - Supports multiple load types

### `api_utils.py`

REST API utilities:

- **`fetch_api_data(api_url, timeout)`**
  - Fetches JSON data from API
  - Handles errors and retries
  - Returns parsed JSON response

### `drive_utils.py`

OnlyOffice file handling utilities:

- **`download_file_from_only_office(file_url, filename, token, password)`**
  - Downloads files from OnlyOffice servers
  - Supports basic authentication with token and password
  - Saves file to `/tmp/` directory

- **`read_file_from_only_office(downloaded_file_path, format)`**
  - Reads downloaded files (CSV, XLSX, XLS formats)
  - Automatically adds `updated_at` timestamp column
  - Returns pandas DataFrame with cleaned data
  - Parameters: `downloaded_file_path`, `format` (csv/xlsx/xls)

### `notif_utils.py`

Slack notification utilities:

- **`construct_failure_message(context)`**
  - Constructs formatted Slack message payload for DAG failures
  - Extracts task information (dag_id, run_id, task_id, timestamps)
  - Includes exception details and formatted status
  - Used for failure callbacks to send alerts to Slack

## DAG Factory

### How It Works

The `DagFactory` class in `dag_factory.py` automatically generates DAGs from JSON configuration files:

1. **Reads JSON files** from `dags/jobs/` directory
2. **Parses configuration** including:
   - DAG metadata (owner, retries, schedule)
   - Job definitions (function type, source, destination, load mode, task_id)
   - Task dependencies specified by task_id
3. **Creates tasks** using the specified `task_id` from configuration
4. **Sets up dependencies** between tasks based on `depends_on` field containing task_ids
5. **Registers DAGs** in Airflow's global namespace

### Adding a New DAG

1. Create a new JSON file in `dags/jobs/` (e.g., `dags/jobs/hourly.json`)
2. Define DAG configuration and jobs
3. Restart Airflow scheduler
4. New DAG appears in Airflow UI automatically

### Example: Adding a New Task to Existing DAG

To add a task to `pipeline_daily`, edit `dags/jobs/daily.json`:

```json
"jobs": [
    { ... existing jobs ... },
    {
        "task_id": "pg_to_pg_new_target",
        "function": "pg_to_pg",
        "source_conn_id": "pg-bssn-sources",
        "target_conn_id": "pg-bssn-dwh",
        "src": "public.new_source",
        "dst": "public.new_target",
        "load_type": "upsert",
        "keys": ["id"],
        "depends_on": ["dwh_to_dwh_joined_data_dst"]
    }
]
```

The factory will use the specified `task_id` and set dependency on the task with `task_id` "dwh_to_dwh_joined_data_dst".

## Docker Services

The setup includes:
- **Airflow WebServer** - UI for managing workflows (port 8080)
- **Airflow Scheduler** - Schedules DAG execution
- **PostgreSQL** - Metadata store and data warehouse
- **Redis** - Message broker for Celery executor
- **Flower** - Celery task monitoring UI (port 5555)

## Logs

DAG execution logs are stored in the `logs/` directory, organized by:
```
logs/dag_id=<dag_name>/run_id=<run_timestamp>/task_id=<task_name>/
```

## Troubleshooting

- **Cannot connect to PostgreSQL:** Verify connection ID and credentials in Airflow UI
- **DAG not appearing:** Check `dags/` folder permissions and PYTHONPATH
- **Task failures:** Review logs in Airflow UI or check Docker container logs
- **Memory issues:** Adjust `docker-compose.yaml` resource limits

## Additional Resources

- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [Airflow PostgreSQL Provider](https://airflow.apache.org/docs/apache-airflow-providers-postgres/)
- [Docker Documentation](https://docs.docker.com/)
