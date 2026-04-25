# DSA Data Extraction with Docker

This repository contains a Docker-based setup for extracting daily dumps from the EU DSA Transparency Database with the `dsa-tdb` toolchain. The workflow builds a container image from the `dsa-tdb/` subdirectory, starts the required services with Docker Compose, and writes the downloaded data to a host-mounted output directory.

## Scope

The documented extraction run in this repository targeted the full 2025 reporting year for two platforms: TikTok and X. The output was stored as platform-specific folders and includes a `parameters.yaml` file per platform that records the selected platform, version, date range, chunking settings, and integrity-check options.

## Prerequisites

Install the following on the host machine:

- Docker Engine or Docker Desktop with Docker Compose support
- Git

No local Python installation is required for the containerized workflow.

## Repository Layout

The actual containerized extractor lives in [dsa-tdb/](dsa-tdb/):

- [dsa-tdb/docker-compose.yml](dsa-tdb/docker-compose.yml) defines the services, volume mounts, port mappings, and DNS settings.
- [dsa-tdb/Dockerfile](dsa-tdb/Dockerfile) builds the application image.
- [dsa-tdb/.env.template](dsa-tdb/.env.template) defines the host-user variables used by the container.
- [dsa-tdb/scripts/download_platform.sh](dsa-tdb/scripts/download_platform.sh) is a helper wrapper around the CLI.
- [dsa-tdb/pyproject.toml](dsa-tdb/pyproject.toml) defines the Python package, the CLI entry point, and runtime dependencies.

## How the Container Is Orchestrated

The Compose file starts three services:

- `redis-docker-service` as the Redis backend.
- `dsa-tdb-docker-service` as the main application container.
- `superset-docker-service` for the bundled dashboard.

The application and dashboard containers both mount a host directory into `/data` inside the container. By default, the host path is `./data`, but it can be overridden with `DOCKER_DATA_DIR`. The Compose file also exposes DNS resolvers (`1.1.1.1` and `8.8.8.8`) for the services.

## Step 1: Prepare the Working Directory

Clone the repository and change into the root folder:

```powershell
git clone <repository-url>
cd Bachelor-Arbeit
```

If you want the container to write data with your host user permissions, copy the environment template and adjust the values:

```powershell
Copy-Item dsa-tdb\.env.template dsa-tdb\.env
```

The template defines these values:

```dotenv
DOCKER_USER=user
DOCKER_USER_ID=1000
DOCKER_GROUP_ID=1000
```

## Step 2: Build the Image

Build the container image from the `dsa-tdb/` directory:

```powershell
Set-Location dsa-tdb
docker-compose build
```

If your Docker installation uses the newer plugin syntax, `docker compose build` is the equivalent command.

## Step 3: Start the Services

Start Redis, the DSA application container, and Superset:

```powershell
docker-compose up -d
```

The application container is exposed as the Compose service `dsa-tdb-docker-service` and the runtime container name `dsa-tdb-api`.

## Step 4: Run the Data Extraction

Open a shell inside the application container and run the `dsa-tdb` CLI.

For the thesis run documented in this repository, the recorded parameters were:

- platform: `tiktok` or `x`
- version: `full`
- date range: `2025-01-01` to `2025-12-31`
- chunk format: `parquet`
- chunk size: `1000000`
- number of processes: `1`
- delete original dumps: `false`

TikTok:

```powershell
docker-compose exec dsa-tdb-docker-service bash -lc "dsa-tdb-cli preprocess -o /data -p tiktok -v full -i 2025-01-01 -f 2025-12-31 --loglevel INFO -n 1 --chunk_size 1000000 --format parquet"
```

X:

```powershell
docker-compose exec dsa-tdb-docker-service bash -lc "dsa-tdb-cli preprocess -o /data -p x -v full -i 2025-01-01 -f 2025-12-31 --loglevel INFO -n 1 --chunk_size 1000000 --format parquet"
```

The same extraction can also be launched with the helper script:

```powershell
docker-compose exec dsa-tdb-docker-service bash -lc "bash ./scripts/download_platform.sh tiktok full /data"
docker-compose exec dsa-tdb-docker-service bash -lc "bash ./scripts/download_platform.sh x full /data"
```

## Step 5: Verify the Outputs

After the extraction completes, the host-mounted data directory contains one folder per platform and version:

- `data/tiktok___full/`
- `data/x___full/`

Each folder contains the daily dump files, the chunked parquet output, and a `parameters.yaml` provenance file.

To check the result on Windows PowerShell:

```powershell
Get-ChildItem .\data\tiktok___full
Get-ChildItem .\data\x___full
```

In the recorded run, both platform folders contained 365 daily files for 2025.

## Stop the Stack

To stop the containers when you are done:

```powershell
docker-compose down
```

## Notes on Output Structure

The output folders use the `platform___version` naming convention from the CLI. The daily downloads are stored as ZIP files, and the processed dataset is written in Parquet format when `--format parquet` is used. The pipeline also writes checksum/provenance metadata alongside the extracted data so that the run can be reproduced and audited later.

## License

The `dsa-tdb` code is licensed under the European Union Public Licence v1.2. The underlying DSA Transparency Database data is licensed under CC BY 4.0.