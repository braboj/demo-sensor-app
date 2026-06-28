# Base image — pinned, current (3.9 reached EOL Oct 2025).
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# The package lives under src/ (src layout); put it on the import path so
# `sensor_api` resolves for gunicorn, flask db, and the worker.
ENV PYTHONPATH=/app/src

# Install dependencies first for better layer caching.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (see .dockerignore for exclusions).
COPY . .

# Expose the application port
EXPOSE 5000

# Run under gunicorn — never the Flask dev server. Settings (bind $PORT, worker
# count, optional in-process generator) live in gunicorn.conf.py so the same
# image serves compose and the cloud. The data generator runs as a separate
# worker service by default (python -m sensor_api.worker); Render free overrides
# this CMD with render-start.sh (migrate + gunicorn) and enables the in-process
# generator via RUN_INPROCESS_GENERATOR.
CMD ["gunicorn", "-c", "gunicorn.conf.py", "sensor_api:create_app()"]
