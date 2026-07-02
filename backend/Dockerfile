# syntax=docker/dockerfile:1

# --- Build stage: install dependencies into an isolated prefix ---------------
# Base image — pinned, current (3.9 reached EOL Oct 2025).
FROM python:3.12-slim AS builder

WORKDIR /app

# Install dependencies into /install so only the built artifacts — not pip's
# caches or build tooling — are carried into the runtime image.
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# --- Runtime stage: slim image, non-root user --------------------------------
FROM python:3.12-slim

WORKDIR /app

# The package lives under src/ (src layout); put it on the import path so
# `sensor_api` resolves for gunicorn, flask db, and the worker. Skip .pyc
# writes (the site-packages are read-only to the non-root user) and keep
# stdout unbuffered so JSON logs reach the runtime promptly.
ENV PYTHONPATH=/app/src \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Bring in the dependencies installed in the build stage (packages land on the
# default site-packages path; console scripts — gunicorn, flask, alembic — on
# PATH under /usr/local/bin).
COPY --from=builder /install /usr/local

# Copy application code (see .dockerignore for exclusions).
COPY . .

# Run as an unprivileged user rather than root. A high, fixed UID keeps the
# image friendly to platforms that run containers under an arbitrary user.
RUN useradd --no-create-home --uid 10001 appuser \
    && chown -R appuser /app
USER appuser

# Expose the application port
EXPOSE 5000

# Run under gunicorn — never the Flask dev server. Settings (bind $PORT, worker
# count, optional in-process generator) live in gunicorn.conf.py so the same
# image serves compose and the cloud. The data generator runs as a separate
# worker service by default (python -m sensor_api.worker); Render free overrides
# this CMD with render-start.sh (migrate + gunicorn) and enables the in-process
# generator via RUN_INPROCESS_GENERATOR.
CMD ["gunicorn", "-c", "gunicorn.conf.py", "sensor_api:create_app()"]
