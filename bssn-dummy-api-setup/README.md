# BSSN Dummy API Server

A small FastAPI-based mock server used by the Airflow DAGs to
simulate external endpoints. It returns fixed JSON payloads and a few
randomised results so you can develop and test workflows without
internet dependencies.

## Repository structure

```
bssn-dummy-api-setup/
├── Dockerfile             # image definition for the mock server
├── Makefile               # convenience target for building the image
├── start.sh               # simple shell helper (alias for `docker build`)
├── dummy_api.py           # FastAPI application defining endpoints
└── README.md              # this documentation
```

The container expects static JSON under `/app/data`; those files are baked
into the image during the build process (see `Dockerfile`).

## Setup Instructions

### Build and run the API server

1. `cd` into the project root:
   ```bash
   cd bssn-dummy-api-setup
   ```

2. Build the Docker image:
   ```bash
   make build-test-api
   ```
   (the `start.sh` script performs the same build).

3. Run the image locally or as part of your Airflow `docker-compose`
   setup – the DAGs assume the service is reachable at
   `http://dummy-api-server:8000`.

```bash
# example: bring up the service with Docker Compose in the airflow
# workspace (see airflow/docker-compose.yaml for network aliases)
docker-compose up -d dummy-api-server
```

