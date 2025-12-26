#!/bin/bash
set -e

echo "Waiting for database to be ready..."
until python -c "import MySQLdb; MySQLdb.connect(host=\"$DB_HOST\", user=\"$DB_USER\", passwd=\"$DB_PASSWORD\", db=\"$DB_NAME\", port=$DB_PORT)" 2>/dev/null; do
  echo "Database is unavailable - sleeping"
  sleep 1
done

echo "Database is ready!"
echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput || true

echo "Starting server..."
exec python manage.py runserver 0.0.0.0:8000

