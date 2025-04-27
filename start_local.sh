#!/bin/bash
# Script to start both the app and worker processes for local development

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed. Please install it first."
    exit 1
fi

# Check if virtual environment exists, if not create it
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if PostgreSQL is running
if ! pg_isready -q; then
    echo "PostgreSQL is not running. Please start PostgreSQL first."
    exit 1
fi

# Check if the database exists, if not create it
if ! psql -lqt | cut -d \| -f 1 | grep -qw webhooks; then
    echo "Creating 'webhooks' database..."
    createdb webhooks
fi

# Check if Redis is running
if ! redis-cli ping > /dev/null 2>&1; then
    echo "Redis is not running. Please start Redis first."
    exit 1
fi

# Start the application and worker in separate terminals
echo "Starting the application and worker..."
osascript -e 'tell app "Terminal" to do script "cd '"$(pwd)"' && source venv/bin/activate && python run_local.py app"'
osascript -e 'tell app "Terminal" to do script "cd '"$(pwd)"' && source venv/bin/activate && python run_local.py worker"'

echo "Application started!"
echo "App running at: http://localhost:8000"
echo "Worker running in background"