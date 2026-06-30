# Onboarding

Get a working `sensor_app` development environment. For day-to-day
commands see [PLAYBOOK.md](PLAYBOOK.md); for conventions see
[CLAUDE.md](../CLAUDE.md).

## What it is

Five services: an Angular SPA, a Flask REST API, a PostgreSQL database, a
standalone worker that simulates sensor readings, and Grafana (datasource +
dashboard provisioned as code from `deploy/grafana/provisioning/`).

```
[ Angular SPA ] --HTTP/JSON--> [ Flask API ] --SQLAlchemy--> [ PostgreSQL ]
   :4200 (nginx)                 :5000 (gunicorn)               :5432
                                      ^                            ^
                                 [ worker ] (data generator)      |
                                                            [ Grafana ] :3000
```

## Prerequisites

- **Docker** + Docker Compose — the only requirement to run the full stack.
- **git**.

For local (non-Docker) development of a single service:

- **Backend:** Python 3.12.
- **Frontend:** Node.js 22 + npm.

## Run the whole stack

```bash
git clone https://github.com/braboj/sensor-data-app
cd sensor-data-app
docker compose up --build
```

This starts `db` → `migrate` (applies Alembic migrations) → `backend` +
`worker` → `frontend`. Then:

- Frontend: http://localhost:4200
- API: http://localhost:5000/api/v1/sensors
- Liveness/readiness: http://localhost:5000/health , `/ready`

## Configuration

The backend reads all config from environment variables (see
`backend/src/sensor_api/config.py`). `docker compose` sets these for you;
for local runs, export them or create `backend/.env`.

| Variable | Purpose | Example |
| --- | --- | --- |
| `APP_CONFIG` | Config class: `development`/`testing`/`production` | `development` |
| `DATABASE_URL` | SQLAlchemy URL | `postgresql+psycopg2://postgres:postgres@db:5432/sensordb` |
| `SECRET_KEY` | Flask secret (set a strong random value) | `change-me` |
| `CORS_ORIGINS` | Comma-separated allowed origins (never `*`) | `http://localhost:4200` |
| `SAMPLE_INTERVAL_SECONDS` | Worker sample interval | `10` |

> A `backend/.env.example` template is the canonical reference; copy it to
> `backend/.env`. Never commit `.env` itself.

## Backend (local, from `backend/`)

```bash
python -m venv .venv && source .venv/Scripts/activate   # Windows Git Bash
pip install -r requirements-dev.txt
export PYTHONPATH=src
flask --app sensor_api db upgrade     # apply migrations
flask --app sensor_api run            # dev server (or: python run.py)
python -m sensor_api.worker           # run the data generator
pytest                                # tests
ruff check .                          # lint
```

## Frontend (local, from `frontend/`)

```bash
npm ci
npm start          # dev server (ng serve)
npm run build      # production build -> dist/sensor-app
npm test           # Karma + Jasmine (headless Chrome)
npm run lint       # ESLint
npm run format     # Prettier (write) / format:check
```

## Quality gates

Install the local pre-commit hooks so you catch issues before pushing:

```bash
pip install pre-commit && pre-commit install
```

See [PLAYBOOK.md](PLAYBOOK.md#local-quality-gates-pre-commit) for details.
