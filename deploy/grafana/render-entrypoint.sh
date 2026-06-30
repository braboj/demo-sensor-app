#!/bin/sh
# Render entrypoint for Grafana.
#
# Two jobs before handing off to Grafana's own /run.sh:
#
# 1. Bind Render's injected $PORT. Grafana reads GF_SERVER_HTTP_PORT; Render
#    assigns the port dynamically, so map one to the other here (default 3000
#    keeps parity with the compose stack and local runs).
#
# 2. Derive the datasource connection. Render's managed Postgres is exposed to
#    other services as a single connection string (the Blueprint sets
#    DATABASE_URL from `fromDatabase: connectionString` — `host`/`port` are not
#    individually referenceable). The provisioned datasource.yaml interpolates
#    POSTGRES_HOST/PORT/USER/PASSWORD/DB, so parse them out of DATABASE_URL.
#    When DATABASE_URL is unset (docker-compose), the POSTGRES_* vars are passed
#    directly and this block is skipped.
set -e

export GF_SERVER_HTTP_PORT="${PORT:-3000}"

if [ -n "${DATABASE_URL:-}" ]; then
  # Strip the scheme (postgres:// or postgresql://[+driver]).
  no_scheme="${DATABASE_URL#*://}"
  # Split "user:password" from "host[:port]/db[?params]" at the last '@'.
  creds="${no_scheme%@*}"
  hostsec="${no_scheme##*@}"
  export POSTGRES_USER="${creds%%:*}"
  export POSTGRES_PASSWORD="${creds#*:}"
  # host[:port] is everything before the first '/'.
  hostport="${hostsec%%/*}"
  export POSTGRES_HOST="${hostport%%:*}"
  if [ "$hostport" != "${hostport#*:}" ]; then
    export POSTGRES_PORT="${hostport##*:}"
  else
    export POSTGRES_PORT="5432"
  fi
  # database is between the first '/' and any '?query'.
  dbsec="${hostsec#*/}"
  export POSTGRES_DB="${dbsec%%\?*}"
  # Render Postgres requires SSL; allow an override for other hosts.
  export POSTGRES_SSLMODE="${POSTGRES_SSLMODE:-require}"
fi

exec /run.sh "$@"
