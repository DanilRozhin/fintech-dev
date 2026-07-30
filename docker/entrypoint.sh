#!/bin/sh
set -e

echo "Waiting for postgres at ${APP_CONFIG__DB__HOST}:${APP_CONFIG__DB__PORT}..."
until nc -z "${APP_CONFIG__DB__HOST}" "${APP_CONFIG__DB__PORT}"; do
  sleep 0.5
done
echo "Postgres is reachable."

echo "Running migrations..."
alembic upgrade head

echo "Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8080
