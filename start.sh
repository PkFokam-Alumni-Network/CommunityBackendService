#!/bin/bash
set -e

echo "Waiting for PostgreSQL to start..."
while ! pg_isready -h db -p 5432 -U postgres; do
  sleep 1
done
echo "PostgreSQL started"

# Run database migrations
alembic upgrade head

# Start the FastAPI app
exec uvicorn main:app --host 0.0.0.0 --port 9000 --proxy-headers --forwarded-allow-ips "*"
