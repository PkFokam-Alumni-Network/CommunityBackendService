#!/bin/sh
set -e

# Only run cleanup and baseline setup in development
# if [ "$ENV" = "development" ]; then
#   echo "DEV mode detected: resetting Alembic migration state"

#   # Remove old migration files (safe for dev)
#   rm -rf alembic/versions/*
#   alembic revision --autogenerate -m "dev baseline schema"
#   alembic stamp head
# fi

# Run Alembic migrations (no-op in dev after stamp)
echo "Running migrations..."
alembic upgrade head || echo "Alembic upgrade failed (already applied?)"

# Start the app
echo "Starting FastAPI..."
exec uvicorn main:app --host 0.0.0.0 --port 9000 --proxy-headers --forwarded-allow-ips "*"
