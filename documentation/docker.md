# Docker Setup

## Overview
This document provides details about the Docker setup for the project, including the purpose of each Docker-related file and how to use them.

### Key Files

#### `Dockerfile`
- **Purpose**: Defines the Docker image for the main application.
- **Key Instructions**:
  - `FROM python:3.11`: Uses Python 3.11 as the base image.
  - `COPY . /app`: Copies the application code into the container.
  - `RUN pip install -r requirements.txt`: Installs Python dependencies.
  - `CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]`: Starts the FastAPI application.

#### `Dockerfile.worker`
- **Purpose**: Defines the Docker image for the background worker process.
- **Key Instructions**:
  - Similar to `Dockerfile`, but the `CMD` instruction starts the worker process instead of the main application.

#### `docker-compose.yml`
- **Purpose**: Configures and manages multiple Docker services.
- **Services**:
  - `app`: Runs the main FastAPI application.
  - `worker`: Runs the background worker process.
  - `db`: Runs the PostgreSQL database.
  - `redis`: Runs the Redis cache.
- **Key Features**:
  - Volume mounting for code changes to reflect without rebuilding the image.
  - Environment variable configuration for each service.

### Usage

#### Build and Start Services
```bash
# Build and start all services
docker-compose up --build
```

#### Stop Services
```bash
# Stop all running services
docker-compose down
```

#### Access Logs
```bash
# View logs for a specific service
docker-compose logs <service_name>
```

#### Execute Commands in a Running Container
```bash
# Access the app container's shell
docker exec -it <container_id> /bin/bash
```

### Local Development Setup

For local development, you can run the application and worker without Docker using the provided scripts.

#### Prerequisites
- Python 3.11 installed on your system.
- PostgreSQL and Redis services running locally.
- Install dependencies using:
  ```bash
  pip install -r requirements.txt
  ```

#### Running the Application Locally
1. Start the FastAPI application:
   ```bash
   python run_local.py
   ```
   This will start the application on `http://127.0.0.1:8000`.

2. Start the worker process:
   ```bash
   python app/worker.py
   ```

#### Environment Variables
Ensure the following environment variables are set in a `.env` file or your shell:
- `DATABASE_URL`: Connection string for the PostgreSQL database.
- `REDIS_URL`: Connection string for the Redis cache.

#### Testing
Run the test suite using:
```bash
pytest tests/
```