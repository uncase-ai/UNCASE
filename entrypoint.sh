#!/bin/sh
# UNCASE entrypoint — run Alembic migrations then start the API server.
set -e

export PATH="/app/.venv/bin:$PATH"

echo "Running database migrations..."
if /app/.venv/bin/python -m alembic upgrade head; then
    echo "Migrations completed successfully."
else
    echo "WARNING: Migrations failed (exit $?). Starting API anyway..."
fi

echo "Starting UNCASE API..."
exec /app/.venv/bin/uvicorn uncase.api.main:app \
    --host 0.0.0.0 \
    --port "${PORT:-8000}" \
    --workers "${WORKERS:-4}"
