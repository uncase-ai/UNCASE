#!/bin/sh
# UNCASE entrypoint — run Alembic migrations then start the API server.
set -e

echo "Running database migrations..."
if /app/.venv/bin/python -m alembic upgrade head; then
    echo "Migrations completed successfully."
else
    echo "WARNING: Migrations failed (exit $?). Starting API anyway..."
fi

echo "Starting UNCASE API..."
exec "$@"
