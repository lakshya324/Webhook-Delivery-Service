# Application Structure

## Overview
This document explains the folder and file organization of the project, providing a clear understanding of its components and their purposes.

### Directory Structure

#### `app/`
- **Purpose**: Contains the main application logic.
- **Subdirectories**:
  - `api/`: Defines API routes and endpoints.
    - `endpoints/`: Contains specific API endpoint implementations (e.g., `subscriptions.py`, `webhooks.py`, `stats.py`).
    - `routes.py`: Aggregates and organizes all API routes.
  - `core/`: Core configurations and utilities.
    - `config.py`: Application settings and environment configurations.
    - `database.py`: Database connection and session management.
    - `cache.py`: Redis caching utilities.
  - `crud/`: Handles database operations (Create, Read, Update, Delete).
    - `delivery.py`: CRUD operations for delivery logs.
    - `subscription.py`: CRUD operations for subscriptions.
    - `webhook.py`: CRUD operations for webhook payloads.
  - `services/`: Business logic and services.
    - `delivery_service.py`: Handles webhook delivery processing.
  - `static/`: Static files such as CSS and JavaScript.
  - `templates/`: HTML templates for rendering the UI.
- **Files**:
  - `main.py`: Entry point for the FastAPI application.
  - `models.py`: SQLAlchemy models for database tables.
  - `schemas.py`: Pydantic schemas for data validation and serialization.
  - `worker.py`: Background worker for processing webhook deliveries.

#### `alembic/`
- **Purpose**: Manages database migrations.
- **Key Files**:
  - `env.py`: Configures Alembic to use the application's database models.
  - `versions/`: Stores migration scripts (e.g., `initial_migration.py`).

#### `tests/`
- **Purpose**: Contains test cases for the application.
- **Key Files**:
  - `test_api.py`: Unit tests for API endpoints.

#### `documentation/`
- **Purpose**: Stores project documentation.
- **Key Files**:
  - `api_endpoints.md`: Details API endpoints.
  - `app_structure.md`: Explains the application structure.
  - `database_structure.md`: Describes the database schema and migrations.
  - `models.md`: Documents the data models.

### Key Files in Root Directory

- **`Dockerfile`**: Defines the Docker image for the application.
- **`Dockerfile.worker`**: Defines the Docker image for the worker process.
- **`docker-compose.yml`**: Configures Docker services (app, worker, database, Redis).
- **`requirements.txt`**: Lists Python dependencies.
- **`run_local.py`**: Script to run the application locally.
- **`start_local.sh`**: Script to start both the app and worker processes for local development.
- **`entrypoint.sh`**: Entry point script for the Docker container.
- **`worker-entrypoint.sh`**: Entry point script for the worker Docker container.