#!/bin/sh

set -e

# Wait for the database to be ready
echo "Waiting for database to be ready..."
python -c '
import time
import psycopg2
import os

db_params = os.environ.get("DATABASE_URL")
if not db_params:
    db_params = "postgresql://postgres:postgres@db:5432/webhooks"

while True:
    try:
        conn = psycopg2.connect(db_params)
        conn.close()
        break
    except psycopg2.OperationalError:
        print("Database not ready, waiting...")
        time.sleep(1)
'

echo "Database is ready!"

# Apply database migrations
echo "Applying database migrations..."
alembic upgrade head

# Start the application
echo "Starting application..."
exec uvicorn main:app --host 0.0.0.0 --port 8000