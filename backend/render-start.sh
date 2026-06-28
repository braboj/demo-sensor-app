#!/usr/bin/env sh
# Render free-tier backend entrypoint.
#
# Render's free instances do not run a separate pre-deploy command, so the
# single web service applies the Alembic migrations itself before serving. The
# upgrade is idempotent, so running it on every boot is safe. Then we exec
# gunicorn (binding $PORT and, when RUN_INPROCESS_GENERATOR is set, starting the
# in-process generator — see gunicorn.conf.py). Compose keeps its own dedicated
# `migrate` and `worker` services and never uses this script.
set -e

flask --app sensor_api db upgrade
exec gunicorn -c gunicorn.conf.py "sensor_api:create_app()"
