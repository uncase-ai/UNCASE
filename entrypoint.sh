#!/bin/sh
# UNCASE entrypoint — run Alembic migrations then start the API server.
set -e

# Ensure venv is on PATH (sh doesn't inherit Docker ENV)
export PATH="/app/.venv/bin:$PATH"

echo "Running database migrations..."
alembic upgrade head

echo "Starting UNCASE API..."
exec "$@"
