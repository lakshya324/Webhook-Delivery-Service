#!/usr/bin/env python3
"""
Local development script to run the application without Docker.
Usage:
    python run_local.py app  # Run the main FastAPI application
    python run_local.py worker  # Run the worker process
"""

import os
import sys
import subprocess
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def run_app():
    """Run the FastAPI application using uvicorn."""
    print("Starting the FastAPI application...")
    subprocess.run(["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"])

def run_worker():
    """Run the worker process."""
    print("Starting the worker process...")
    subprocess.run(["python", "-m", "app.worker"])

def setup_database():
    """Run alembic migrations to set up the database."""
    print("Running database migrations...")
    subprocess.run(["alembic", "upgrade", "head"])
    print("Database migrations completed!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please specify a command: 'app' or 'worker'")
        sys.exit(1)
    
    command = sys.argv[1]
    
    # Setup database first
    if command == "app":
        setup_database()
        run_app()
    elif command == "worker":
        run_worker()
    else:
        print(f"Unknown command: {command}")
        print("Available commands: 'app' or 'worker'")
        sys.exit(1)