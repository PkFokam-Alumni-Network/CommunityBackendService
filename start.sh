#!/bin/bash
set -e



# Run database migrations
# alembic upgrade head

# Start the FastAPI app
exec uvicorn main:app --host 0.0.0.0 --port 9000 --proxy-headers --forwarded-allow-ips "*"
