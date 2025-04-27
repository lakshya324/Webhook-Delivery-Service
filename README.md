# Webhook Delivery Service Documentation

## Overview
The Webhook Delivery Service is a FastAPI-based application designed to manage webhook subscriptions, ingest webhooks, and track delivery attempts. It provides a user-friendly interface and API endpoints for seamless integration.

## Features
- **Subscription Management**: Create, edit, and delete webhook subscriptions.
- **Webhook Ingestion**: Send and process webhooks with payloads.
- **Delivery Tracking**: Monitor delivery attempts and view detailed logs.
- **Statistics**: Analyze webhook delivery performance.
- **Interactive API Documentation**: Access `/docs` (Swagger UI) and `/redoc` (ReDoc) for API exploration.

## Project Structure
For a detailed explanation of the project structure, refer to the [Application Structure Documentation](documentation/app_structure.md).

```
app/
├── api/                # API routes and endpoints
├── core/               # Core configurations and utilities
├── crud/               # Database operations
├── services/           # Business logic and services
├── templates/          # HTML templates for the UI
├── static/             # Static files (e.g., CSS)
├── models.py           # Database models
├── schemas.py          # Pydantic schemas
├── main.py             # Application entry point
├── worker.py           # Background worker for processing tasks

alembic/                # Database migrations

Dockerfile              # Docker configuration
requirements.txt        # Python dependencies
```

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL
- Redis
- Docker (optional for containerized deployment)

### Local Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/lakshya324/Webhook-Delivery-Service.git
   cd Webhook-Delivery-Service
   ```

2. Create a virtual environment and activate it:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```bash
   alembic upgrade head
   ```

5. Start the application locally:
   ```bash
   python run_local.py app
   ```

6. Start the worker process:
   ```bash
   python run_local.py worker
   ```

7. Access the application:
   - API Documentation (Swagger UI): [http://localhost:8000/docs](http://localhost:8000/docs)
   - API Documentation (ReDoc): [http://localhost:8000/redoc](http://localhost:8000/redoc)

For more details on the database schema and migrations, refer to the [Database Structure Documentation](documentation/database_structure.md).

### Docker Setup
1. Build and run the application using Docker:
   ```bash
   docker-compose up --build
   ```

2. Access the application:
   - API Documentation (Swagger UI): [http://localhost:8000/docs](http://localhost:8000/docs)
   - API Documentation (ReDoc): [http://localhost:8000/redoc](http://localhost:8000/redoc)

For more information on Docker setup, refer to the [Docker Documentation](documentation/docker.md).

## API Endpoints
For a detailed list of API endpoints, refer to the [API Endpoints Documentation](documentation/api_endpoints.md).

### Subscriptions
- `GET /api/v1/subscriptions/`: List all subscriptions.
- `POST /api/v1/subscriptions/`: Create a new subscription.
- `PUT /api/v1/subscriptions/{id}`: Update a subscription.
- `DELETE /api/v1/subscriptions/{id}`: Delete a subscription.

### Webhooks
- `POST /api/v1/webhooks/ingest/{subscription_id}`: Ingest a webhook.
- `GET /api/v1/webhooks/{webhook_id}/status`: Get delivery logs for a webhook.

### Statistics
- `GET /api/v1/stats/subscription/{subscription_id}`: Get statistics for a subscription.
- `GET /api/v1/stats/recent-attempts/{subscription_id}`: Get recent delivery attempts.

## Testing
Run the test suite using pytest:
```bash
pytest tests/
```

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

**Created by Lakshya Sharma**