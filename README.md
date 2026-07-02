[![CI](https://github.com/braboj/demo-sensor-app/actions/workflows/ci.yml/badge.svg)](https://github.com/braboj/demo-sensor-app/actions/workflows/ci.yml)
[![CodeQL](https://github.com/braboj/demo-sensor-app/actions/workflows/codeql.yml/badge.svg)](https://github.com/braboj/demo-sensor-app/actions/workflows/codeql.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

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
  empty, and error states; new readings arrive over **Server-Sent Events**
- **Charts** — the embedded Grafana "Sensor Readings" dashboard with a metric
  selector (temperature / humidity / vibration) and a moving-average trend,
  provisioned as code.
- **Versioned REST API** — `/api/v1/sensors` with a bounded `?limit=`, ISO-8601
  UTC timestamps, and RFC 9457 JSON errors; plus `/health` and `/ready`.
- **Sensor Simulator** — the simulator runs as its own worker process, not a
  thread inside the web app.
- **Deployable** — a free-tier [Render blueprint](render.yaml) runs the whole
  stack (see [Deploy](docs/DEPLOY.md)).

## Quick start

Prerequisites:

- [Docker](https://docs.docker.com/engine/install/)
- [git](https://git-scm.com/downloads)

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
provisioned as code (`deploy/grafana/provisioning/`). The admin login is set via
the `GRAFANA_ADMIN_USER` / `GRAFANA_ADMIN_PASSWORD` environment variables (see
`docker-compose.yml`) — set your own before exposing Grafana beyond local use.

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

## Project structure

| Path | Purpose |
|------|---------|
| `backend/` | Flask REST API + data-generator worker |
| `backend/src/sensor_api/` | App factory, config, blueprints (sensors, health), worker |
| `backend/migrations/` | Alembic migrations |
| `backend/tests/` | pytest suite |
| `frontend/` | Angular SPA (standalone components) |
| `frontend/src/app/home/` | Live readings table + SSE |
| `frontend/src/app/charts/` | Embedded Grafana dashboard |
| `frontend/src/environments/` | API / Grafana URLs (dev + prod) |
| `deploy/grafana/` | Grafana image + datasource/dashboard provisioned as code |
| `docs/` | ONBOARDING, PLAYBOOK, DEPLOY, decisions (ADRs), history |
| `docs/arc42/` | Architecture documentation (arc42) |
| `docker-compose.yml` | Full local stack (backend, frontend, db, grafana, worker) |
| `render.yaml` | Render free-tier blueprint |

## Development

`docker compose up` (above) runs the whole stack. To work on a service on its
own — PostgreSQL is the only external dependency (`docker compose up db` starts
one):

Backend (Python 3.12, from `backend/`):

```bash
pip install -r requirements.txt
pytest && mypy src --strict          # tests + strict type check
flask --app sensor_api run           # dev server (needs a reachable PostgreSQL)
python -m sensor_api.worker          # run the data generator
```

Frontend (Node 22, from `frontend/`):

```bash
npm ci
npm start                            # ng serve on :4200
npm test && npx eslint .             # unit tests + lint
```

The backend reads its configuration from environment variables — copy the
committed `backend/.env.example` to `backend/.env` and adjust. See
[Onboarding](docs/ONBOARDING.md) for full setup and [Playbook](docs/PLAYBOOK.md)
for day-to-day commands.

## Configuration

Services are configured through environment variables (documented in
`backend/.env.example` and [`docker-compose.yml`](docker-compose.yml)); the most
important:

| Variable | Service | Default | Description |
|----------|---------|---------|-------------|
| `DATABASE_URL` | backend, grafana | — | PostgreSQL connection string. |
| `SECRET_KEY` | backend | — | Flask secret key (**sensitive** — set your own). |
| `CORS_ORIGINS` | backend | — | Allowed frontend origin (never `*`). |
| `APP_CONFIG` | backend | `production` | Config profile (`development` / `production`). |
| `SAMPLE_INTERVAL_SECONDS` | backend, worker | `10` | Generator sample interval. |
| `RUN_INPROCESS_GENERATOR` | backend | `false` | Run the generator in-process (free-tier only). |
| `WEB_CONCURRENCY` | backend | `1` | gunicorn worker count. |
| `API_URL` | frontend (build) | same-origin `/api/v1/sensors` | Absolute backend URL baked into the bundle. |
| `GRAFANA_URL` | frontend (build) | empty | Grafana dashboard URL for the Charts view. |
| `GRAFANA_ADMIN_USER` / `GRAFANA_ADMIN_PASSWORD` | grafana | — | Local admin login (**sensitive**). |

See [Deploy](docs/DEPLOY.md) for the full deployment variable set.

## Deploy

The repo ships a [`render.yaml`](render.yaml) blueprint that runs the whole
stack on Render's free tier — managed Postgres, the Dockerized backend, the
static frontend, and Grafana. The live demo above runs from this blueprint. See
[Deploy](docs/DEPLOY.md) for the walkthrough and the free-tier caveats.

## Next steps

- To understand the architecture, see the [Architecture docs (arc42)](docs/arc42/README.md)
- To set up a dev environment, see [Onboarding](docs/ONBOARDING.md)
- For day-to-day commands, see the [Playbook](docs/PLAYBOOK.md)
- To deploy on Render (free tier), see [Deploy](docs/DEPLOY.md)
- To learn more about the project, see the [Assignment](docs/history/ASSIGNMENT.md)
- To read about the solution, see the [Solution](docs/history/SOLUTION.md)
- To contribute, see [Contributing](CONTRIBUTING.md)
- To leave feedback, visit [Discussions](https://github.com/braboj/demo-sensor-app/discussions)

## License

Licensed under the [MIT License](LICENSE).
