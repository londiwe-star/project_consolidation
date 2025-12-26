# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        default-libmysqlclient-dev \
        pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Create necessary directories
RUN mkdir -p /app/staticfiles /app/media

# Expose port
EXPOSE 8000

# Create entrypoint script with database wait
RUN echo '#!/bin/bash\n\
set -e\n\
echo "Waiting for database to be ready..."\n\
until python -c "import MySQLdb; MySQLdb.connect(host=\"$DB_HOST\", user=\"$DB_USER\", passwd=\"$DB_PASSWORD\", db=\"$DB_NAME\", port=$DB_PORT)" 2>/dev/null; do\n\
  echo "Database is unavailable - sleeping"\n\
  sleep 1\n\
done\n\
echo "Database is ready!"\n\
echo "Running migrations..."\n\
python manage.py migrate --noinput\n\
echo "Collecting static files..."\n\
python manage.py collectstatic --noinput || true\n\
echo "Starting server..."\n\
exec python manage.py runserver 0.0.0.0:8000' > /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh

# Use entrypoint script
CMD ["/app/entrypoint.sh"]

