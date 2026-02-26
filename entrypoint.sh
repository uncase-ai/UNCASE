#!/bin/sh
# UNCASE entrypoint — run Alembic migrations then start the API server.
set -e

echo "Running database migrations..."
/app/.venv/bin/python -m alembic upgrade head

echo "Starting UNCASE API..."
exec "$@"
