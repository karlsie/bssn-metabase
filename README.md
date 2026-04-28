# BSSN Data Platform

Top‑level repository for BSSN data platform infrastructure. This
mono‑repo contains two primary components:

- [Airflow orchestration](/airflow/) – DAGs, utilities, and
  Docker configuration used to run ETL pipelines.
- [Metabase configuration](/metabase/) – static files and service
  definition for running Metabase against the data warehouse.

Each subdirectory has its own README with setup instructions and
usage details; click the links above to get started.

## High‑Level Architecture

The ETL architecture follows a pattern with clear separation between data ingestion, transformation, and consumption layers.
Apache Airflow serves as the orchestration backbone, managing workflow dependencies, scheduling, and monitoring across all data pipeline operations.

![data architecture](images/data%20ETL%20architecture.png)

the component interactions are as follows:

| Layer          | Component            | Technology           |
|----------------|----------------------|----------------------|
| Source Layer   | PostgreSQL Database  | PostgreSQL 13+       |
|                | Excel Files          | XLSX/XLS formats     |
|                | REST API             | HTTP/JSON endpoints  |
| Orchestration  | Workflow Manager     | Apache Airflow       |
| Target Layer   | Data Warehouse       | PostgreSQL 18+       |
| Presentation   | Business Intelligence| Metabase             |
