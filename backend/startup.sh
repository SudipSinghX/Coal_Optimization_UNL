#!/bin/sh
# startup.sh — run Alembic migrations then start the API server.
# This script is the CMD entrypoint for the production Docker image.
set -e

echo "[startup] Running Alembic database migrations..."
alembic upgrade head
echo "[startup] Migrations complete. Starting uvicorn..."

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
