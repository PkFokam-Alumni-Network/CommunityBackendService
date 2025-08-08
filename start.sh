#!/bin/sh
set -e

echo "Running migrations..."
alembic upgrade head || echo "Alembic upgrade failed (already applied?)"

# Start the app
echo "Starting FastAPI..."
exec uvicorn main:app --host 0.0.0.0 --port 9000 --proxy-headers --forwarded-allow-ips "*"
