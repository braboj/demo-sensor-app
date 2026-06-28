# Playbook

Operational commands and workflows for `sensor_app`. New to the project?
Start with [ONBOARDING.md](ONBOARDING.md).

## Full stack (Docker)

```bash
docker compose up --build        # start db, migrate, backend, worker, frontend
docker compose up -d             # detached
docker compose logs -f backend   # follow a service's logs
docker compose down              # stop
docker compose down -v           # stop and wipe the postgres volume
docker compose exec db psql -U postgres -d sensordb   # DB shell
```

Startup order is enforced via healthchecks: `db` → `migrate`
(`flask db upgrade`, runs once) → `backend` + `worker` → `frontend`.

## Backend (from `backend/`)

```bash
export PYTHONPATH=src                          # src layout
flask --app sensor_api run                     # dev server (or: python run.py)
flask --app sensor_api db upgrade              # apply migrations
flask --app sensor_api db migrate -m "msg"     # generate a migration
flask --app sensor_api db downgrade            # roll back one migration
python -m sensor_api.worker                    # run the data generator
pytest                                         # tests
ruff check .                                   # lint
gunicorn "sensor_api:create_app()"             # production server (Linux)
```

### Database migrations

Schema changes ship a reversible Alembic migration — never
`db.create_all()` at runtime. After changing a model:

```bash
flask --app sensor_api db migrate -m "describe the change"   # autogenerate
# review the generated file in migrations/versions/, then:
flask --app sensor_api db upgrade
```

Migrations are committed and applied automatically by the compose
`migrate` service on startup.

## Frontend (from `frontend/`)

```bash
npm ci               # reproducible install
npm start            # dev server
npm run build        # production build -> dist/sensor-app
npm test             # Karma + Jasmine (headless Chrome)
npm run lint         # ESLint
npm run format       # Prettier (write)
npm run format:check # Prettier (check only — used in CI)
```

## Local quality gates (pre-commit)

Layer-2 gates (CLAUDE.md §3.2) mirror CI and run before each commit, so
problems are caught locally before they are pushed.

Install once per clone:

```bash
pip install pre-commit
pre-commit install          # enable the git hook
cd frontend && npm ci       # the eslint/prettier hooks use this toolchain
```

Run manually:

```bash
pre-commit run --all-files  # every hook across the whole repo
pre-commit run ruff-check   # a single hook
pre-commit autoupdate       # bump pinned hook versions
```

Hooks (see [`.pre-commit-config.yaml`](../.pre-commit-config.yaml)):

| Hook | Scope | Mirrors CI |
| --- | --- | --- |
| `ruff-check` | `backend/` Python lint | `ruff check backend` |
| `gitleaks` | secret scan | gitleaks job |
| `eslint` | `frontend/` TS/HTML lint | `npm run lint` |
| `prettier` | `frontend/src` format check | `npm run format:check` |
| `check-yaml`, `check-merge-conflict`, `check-added-large-files` | repo | — |

> **mypy is not enabled yet.** The backend is not fully type-annotated and
> `db.Model` / `flask_migrate` need typing work first — the same reason CI
> defers `mypy --strict`. A mypy hook joins once the annotations land.

## CI

GitHub Actions runs on every PR and push to `main` (see
[`.github/workflows/ci.yml`](../.github/workflows/ci.yml)): backend
(`ruff check` + `pytest`), frontend (`lint` + `format:check` + `build` +
`test`), gitleaks, and CodeQL. `main` is protected — merge via PR on green
CI.

## Deploy (Render free tier)

Deployment is a version-controlled Blueprint, [`render.yaml`](../render.yaml)
(managed Postgres + Docker backend + static frontend). There is no deploy CLI
step — connect the repo once in the Render dashboard (**New + → Blueprint**) and
pushes to the deployed branch auto-deploy. Full walkthrough and free-tier
caveats: [DEPLOY.md](DEPLOY.md).

Verify a running deploy:

```bash
curl https://sensor-app-backend.onrender.com/health    # {"status":"ok"}
curl https://sensor-app-backend.onrender.com/ready     # {"status":"ready"}
curl "https://sensor-app-backend.onrender.com/api/v1/sensors?limit=5"
```

On the free tier the generator runs in-process in the single web instance
(`RUN_INPROCESS_GENERATOR=true`), not as a separate worker — see
[ADR-0004](decisions/0004-inprocess-generator-free-tier.md).
