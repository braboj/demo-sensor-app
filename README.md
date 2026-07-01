[![CI](https://github.com/braboj/demo-sensor-app/actions/workflows/ci.yml/badge.svg)](https://github.com/braboj/demo-sensor-app/actions/workflows/ci.yml)
[![CodeQL](https://github.com/braboj/demo-sensor-app/actions/workflows/codeql.yml/badge.svg)](https://github.com/braboj/demo-sensor-app/actions/workflows/codeql.yml)

# Sensor Dashboard

*A multi-service demo that simulates industrial-plant sensor readings —
generated, stored, streamed live, and charted.*

A Python (Flask) backend generates sensor data via a standalone worker, stores
it in PostgreSQL, and exposes it through a versioned REST API; an Angular
frontend shows a live table and embeds Grafana for charting.

**🌐 Live demo:** <https://sensor-app-frontend.onrender.com> — the **Live Table**
tab streams new readings in real time, and the **Charts** tab embeds the Grafana
dashboard. It runs on Render's free tier, so the first request after a while may
cold-start for ~30–60s.

## Features

- **Live table** — Angular SPA (standalone components) with explicit loading,
  empty, and error states; new readings arrive over **Server-Sent Events**, not
  polling.
- **Charts** — the embedded Grafana "Sensor Readings" dashboard with a metric
  selector (temperature / humidity / vibration) and a moving-average trend,
  provisioned as code.
- **Versioned REST API** — `/api/v1/sensors` with a bounded `?limit=`, ISO-8601
  UTC timestamps, and RFC 9457 JSON errors; plus `/health` and `/ready`.
- **Separate generator** — the simulator runs as its own worker process, not a
  thread inside the web app.
- **One command** — `docker compose up` starts the backend, frontend,
  PostgreSQL, Grafana, and the worker; the schema comes from Alembic migrations.
- **Deployable** — a free-tier [Render blueprint](render.yaml) runs the whole
  stack (see [Deploy](docs/DEPLOY.md)).

## Requirements

To run the application, install:

- [Docker](https://docs.docker.com/engine/install/)
- [git](https://git-scm.com/downloads)

## Quick start

Clone the repository and start the full stack:

```bash
git clone https://github.com/braboj/demo-sensor-app
cd demo-sensor-app
docker compose up
```

This starts the frontend, backend, a PostgreSQL database, a one-shot migration
step, the data-generator worker, and Grafana:

- [Frontend (Angular) / localhost:4200](http://localhost:4200)
- [Backend (Flask) / localhost:5000](http://localhost:5000)
- [Grafana / localhost:3000](http://localhost:3000)

Grafana ships with a PostgreSQL datasource and the "Sensor Readings" dashboard
provisioned as code (`deploy/grafana/provisioning/`). Log in with `admin` /
`admin` (override via `GRAFANA_ADMIN_USER` / `GRAFANA_ADMIN_PASSWORD`).

## Usage

Fetch the most recent readings (the last 100 by default):

```bash
curl http://localhost:5000/api/v1/sensors
```

```json
[
  {
    "id": 1940,
    "timestamp": "2026-07-01T06:27:14.147279+00:00",
    "temperature": 4.4,
    "humidity": 93.14,
    "vibration": 0
  },
  {
    "id": 1939,
    "timestamp": "2026-07-01T06:27:04.139090+00:00",
    "temperature": 11.32,
    "humidity": 92.68,
    "vibration": 1
  }
]
```

Vibration is a coded value: `0` = none, `1` = detected.

Bound the result with `?limit=` (an integer 1–100; a non-integer or
out-of-range value returns `400`, never a silent fallback):

```bash
curl "http://localhost:5000/api/v1/sensors?limit=1"
```

Subscribe to the live stream (Server-Sent Events) — new readings arrive as they
are recorded (see [ADR-0005](docs/decisions/0005-realtime-delivery-sse.md)):

```bash
curl -N http://localhost:5000/api/v1/sensors/stream
```

Operational endpoints: `GET /health` (liveness — 200 if the process is up) and
`GET /ready` (readiness — 200 if the database is reachable, else 503).

## Deploy

The repo ships a [`render.yaml`](render.yaml) blueprint that runs the whole
stack on Render's free tier — managed Postgres, the Dockerized backend, the
static frontend, and Grafana. The live demo above runs from this blueprint. See
[Deploy](docs/DEPLOY.md) for the walkthrough and the free-tier caveats.

## Next steps

- To set up a dev environment, see [Onboarding](docs/ONBOARDING.md)
- For day-to-day commands, see the [Playbook](docs/PLAYBOOK.md)
- To deploy on Render (free tier), see [Deploy](docs/DEPLOY.md)
- To learn more about the project, see the [Assignment](docs/history/ASSIGNMENT.md)
- To read about the solution, see the [Solution](docs/history/SOLUTION.md)
- To contribute, see [Contributing](CONTRIBUTING.md)
- To leave feedback, visit [Discussions](https://github.com/braboj/demo-sensor-app/discussions)
