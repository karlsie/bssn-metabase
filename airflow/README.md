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
│   └── airflow.cfg           # Airflow configuration file
├── dags/
│   ├── pg_to_pg.py          # PostgreSQL to PostgreSQL transfer DAG
│   ├── rest_api_to_postgres.py  # REST API to PostgreSQL ingestion DAG
│   └── utils/
│       ├── __init__.py
│       └── airflow_utils.py  # Shared utility functions
├── logs/                      # DAG execution logs (auto-generated)
├── plugins/                   # Custom plugins directory
├── docker-compose.yaml        # Docker Compose configuration
├── Dockerfile                 # Custom Airflow image (if needed)
├── Makefile                   # Common commands
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Available DAGs

### 1. `postgres_to_postgres_transfer`

Transfers data between PostgreSQL tables with support for full and incremental loads.

**Features:**
- Full table overwrite mode
- Incremental append mode (delta loads based on date column)
- Configurable source/target connections and tables
- Validates date columns for incremental loads

**Parameters:**
- `source_conn_id`: Source PostgreSQL connection ID (default: `bssn-dwh`)
- `target_conn_id`: Target PostgreSQL connection ID (default: `bssn-dwh`)
- `source_table`: Source table name (default: `public.aset_tik`)
- `target_table`: Target table name (default: `public.aset_tik_dt`)
- `load_type`: `overwrite` or `append` (default: `append`)
- `date_column`: Column name for incremental filtering (required for append mode)
- `from_date`: Start date for incremental load (required for append mode)

### 2. `rest_api_to_postgres`

Extracts data from REST APIs and loads into PostgreSQL.

**Features:**
- Configurable API endpoints
- Automatic retry logic (2 retries with 5-minute delays)
- Failure notifications via email
- Single active run (prevents concurrent executions)

**Parameters:**
- `api_url`: REST API endpoint (default: `http://dummy-api-server:8000/nilai_csm`)
- `target_conn_id`: Target PostgreSQL connection ID (default: `bssn-dwh`)
- `target_table`: Target table name (default: `public.nilai_csm`)

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
