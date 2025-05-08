#!/bin/sh

set -e

# Wait for the database and app to be ready
echo "Waiting for services to be ready..."
sleep 10

# Start the worker
echo "Starting webhook worker..."
exec python -m app.worker