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
│   ├── manual_pg_to_pg.py              # manual trigger for pg-to-pg transfer
│   ├── manual_rest_api_to_postgres.py  # manual API ingestion
│   ├── rest_api_to_pg_daily.py         # daily REST API ingestion DAG
│   ├── rest_api_to_pg_monthly.py       # monthly REST API ingestion DAG
│   ├── pg_transfers_daily.py           # daily pg-to-pg transfer DAG
│   ├── pg_transfers_weekly.py          # weekly pg-to-pg transfer DAG
│   ├── values/                         # JSON parameter overrides for DAGs
│   │   ├── api_to_pg_daily.json
│   │   ├── api_to_pg_monthly.json
│   │   ├── pg_to_pg_daily.json
│   │   └── pg_to_pg_weekly.json
│   └── utils/
│       ├── __init__.py
│       └── airflow_utils.py            # Shared utility functions
├── logs/                                # DAG execution logs (auto-generated)
├── plugins/                             # Custom plugins directory
├── docker-compose.yaml                  # Docker Compose configuration
├── Dockerfile                           # Custom Airflow image (if needed)
├── Makefile                             # Common commands
├── requirements.txt                     # Python dependencies
└── README.md                            # This file
```

## Available DAGs

### PostgreSQL‑to‑PostgreSQL Transfers
A pair of parameterized DAGs perform data movement between Postgres tables.

- **`pg_transfers_daily`** – runs every day at 02:00 UTC using definitions in `dags/values/pg_to_pg_daily.json`.
- **`pg_transfers_weekly`** – weekly version, reads `dags/values/pg_to_pg_weekly.json`.
- **`manual_pg_to_pg`** – manual trigger helper for ad‑hoc transfers.

All three call `transfer_postgres_to_postgres` in `airflow_utils.py` and support
`overwrite` or `append` modes. See utility documentation below for full
parameter list.

### REST API Ingestion
Three DAGs for loading JSON APIs into Postgres tables:

- **`rest_api_to_pg_daily`** – pulls daily endpoints; parameters are in
  `dags/values/api_to_pg_daily.json`.
- **`rest_api_to_pg_monthly`** – monthly endpoints using
  `dags/values/api_to_pg_monthly.json`.
- **`manual_rest_api_to_postgres`** – manual runner for development or
testing.

They leverage `load_api_to_postgres` from `airflow_utils.py`.

### Summary of Utility Parameters
Both transfer helpers read arguments via `op_kwargs`, DAG params, or
`dag_run.conf`.

#### `transfer_postgres_to_postgres`
- `source_conn_id`, `target_conn_id` – connection IDs
- `source_table`, `target_table` – schema-qualified table names
- `load_type` – `'overwrite'` or `'append'` (append requires `date_column`
  and `from_date`)
- `date_column`/`from_date` – for incremental loads
- `batch_size` – rows per insert chunk (default 10000)

#### `load_api_to_postgres`
- `api_url` – URL to query
- `target_conn_id`, `target_table` – where to write results

(See function docstrings in `dags/utils/airflow_utils.py` for more.)

## Setup

### Prerequisites

- Docker & Docker Compose
- Make (optional, for convenience commands)

### Installation

1. **Initialize Airflow database and user:**
   ```bash
   make up
   ```
   This runs:
   - `docker-compose up -d airflow-init` - Initializes the database
   - `docker-compose --profile flower up -d` - Starts all services including Flower monitoring

2. **Check service status:**
   ```bash
   make status
   ```

3. **Access Airflow UI:**
   - URL: `http://localhost:8080`
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
- `_AIRFLOW_WWW_USER_USERNAME` - Admin username (default: `airflow`)
- `_AIRFLOW_WWW_USER_PASSWORD` - Admin password (default: `airflow`)

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

Contains shared functions used by DAGs:

- **`transfer_postgres_to_postgres(**context)`**
  - Handles PostgreSQL-to-PostgreSQL data transfers
  - Supports overwrite and append modes
  - Validates schema and date columns

- **`load_api_to_postgres(**context)`**
  - Fetches data from REST APIs
  - Loads data into PostgreSQL tables

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
