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

# Run under gunicorn — never the Flask dev server. The data generator runs
# as a separate worker service (python -m sensor_api.worker), so multiple web
# workers are safe; tune with the WEB_CONCURRENCY env var (gunicorn reads it).
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "sensor_api:create_app()"]
