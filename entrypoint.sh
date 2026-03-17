#!/bin/sh
# UNCASE entrypoint — run Alembic migrations then start the API server.
set -e

export PATH="/app/.venv/bin:$PATH"

echo "Running database migrations..."
if ! /app/.venv/bin/python -m alembic upgrade head; then
    echo "ERROR: Migrations failed. Refusing to start with stale schema."
    exit 1
fi
echo "Migrations completed successfully."

echo "Starting UNCASE API..."
exec /app/.venv/bin/python -m uvicorn uncase.api.main:app \
    --host 0.0.0.0 \
    --port "${PORT:-8000}" \
    --workers "${WORKERS:-1}"
