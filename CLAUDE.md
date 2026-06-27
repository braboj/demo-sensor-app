# Sensor Dashboard (sensor_app)

A multi-service demo that simulates industrial plant sensor readings: a
Flask backend generates and stores data, exposes it over a REST API; an
Angular frontend displays it; PostgreSQL persists it; Grafana visualizes
it.

- Owner: Branimir Georgiev (Imbra.io)
- Repo: github.com/braboj/sensor-data-app
- Deployment: Docker Compose (local); container images per service
- Model: hybrid

> **Purpose of this file.** This is the *target* convention set the
> codebase is being refactored toward — not a description of the current
> code. The current code is an MVP take-home and deviates in several
> places; the gap list is the 360 audit at
> `docs/audits/2026-06-26-360.md`. Refactor toward the rules below.

Quality conventions are defined in `docs/solid-ai-templates/` (vendored
submodule). Critical and project-specific rules are inlined here; the
full framework lives in the templates. Key references in the dependency
chain (`stack-flask` + frontend layer + platform):

- Base: `base/core/{git,docs,quality,readme,testing,oop,config}.md`
- Security: `base/security/{security,devsecops}.md`
- Infra: `base/infra/{containers,cicd}.md`,
  `base/workflow/quality-gates.md`
- Backend: `backend/{http,api,database,observability,monitoring,errors,`
  `concurrency,quality}.md`
- Frontend: `frontend/{ux,quality}.md`, `base/language/typescript.md`
- Platform & process: `platform/github.md`, `base/workflow/scope.md`,
  `base/workflow/360.md`

---

## 1. Project

### 1.1 Overview

- Model: hybrid
- Architecture: four services — `backend`, `frontend`, `db`, `grafana`
- Backend language: Python 3.12 (upgrade off EOL 3.9)
- Backend framework: Flask 3.x (application factory + blueprints)
- ORM / migrations: SQLAlchemy 2.x + Flask-Migrate (Alembic)
- WSGI server (production): gunicorn — never the Flask dev server
- Frontend: Angular 19 (standalone components) + TypeScript 5.x (strict)
- Database: PostgreSQL 16
- Visualization: Grafana (dashboards & datasources provisioned as code)
- Linters/formatters: ruff + ruff format (Python), ESLint + Prettier (TS)
- Type checkers: mypy (strict), Angular strict templates
- Test runners: pytest + pytest-flask (backend), Karma + Jasmine (frontend)
- Orchestration: Docker Compose; one image per service

### 1.2 Service architecture

```
[ Angular SPA ] --HTTP/JSON--> [ Flask REST API ] --SQLAlchemy--> [ PostgreSQL ]
   (frontend:4200)                (backend:5000)                     (db:5432)
                                        |                                ^
                                  data generator                        |
                                  (separate worker)                     |
                                                                  [ Grafana ]
                                                                 (grafana:3000)
                                                              reads from PostgreSQL
```

- The frontend talks only to the backend API — never to the DB directly.
- The sensor data generator is a **separate process/worker**, not a
  thread spawned inside the Flask app factory (see 2.6).
- Grafana reads from PostgreSQL (or a metrics backend) via a
  provisioned, version-controlled datasource — no manual UI config.

### 1.3 Project structure (target)

```
backend/
  src/
    sensor_api/
      __init__.py        # create_app(config=None) factory ONLY
      config.py          # DevelopmentConfig, TestingConfig, ProductionConfig
      extensions.py      # db, migrate instances (init_app inside factory)
      blueprints/
        sensors/
          __init__.py
          routes.py      # /api/v1/sensors
          models.py      # SensorData
          schemas.py     # request/response validation + serialization
          services.py    # query/business logic (no logic in routes)
        health/
          routes.py      # /health (liveness), /ready (readiness)
      sensors/           # sensor simulation domain (AnalogSensor, ...)
      errors.py          # error types + registered Flask error handlers
    worker.py            # standalone data-generator entrypoint (see 2.6)
  migrations/            # Alembic migrations (committed)
  tests/
    conftest.py          # app fixture (TestingConfig), client, test DB
    test_*.py
  pyproject.toml         # ruff, mypy, pytest config
  .env.example           # committed — never .env
  .dockerignore
  Dockerfile             # multi-stage; runs gunicorn
frontend/
  src/
    app/                 # standalone components, services, models
    environments/        # environment.ts / environment.prod.ts (API URL)
  .dockerignore
  Dockerfile             # multi-stage build -> nginx serves dist/
  package.json           # name: sensor-app-frontend; project: sensor-app
deploy/
  grafana/
    provisioning/
      datasources/       # datasource.yaml (Postgres) — as code
      dashboards/        # dashboard provider + JSON dashboards
docs/
  audits/                # 360 audit reports (YYYY-MM-DD-360.md)
  history/               # ASSIGNMENT.md, SOLUTION.md
  solid-ai-templates/    # vendored conventions submodule
  ONBOARDING.md          # (to generate)
  PLAYBOOK.md            # (to generate)
  dev-journal.md         # (to generate)
docker-compose.yml
README.md
CLAUDE.md
```

### 1.4 Commands

```bash
docker compose up                      # full stack: backend+frontend+db+grafana

# Backend (from backend/)
flask --app sensor_api run             # dev server (local only)
flask --app sensor_api db upgrade      # apply migrations
flask --app sensor_api db migrate -m "msg"   # generate a migration
python -m sensor_api.worker            # run the data generator worker
pytest && mypy src/ --strict           # tests + type check
gunicorn "sensor_api:create_app()"     # production server

# Frontend (from frontend/)
npm ci                                 # reproducible install (uses lockfile)
npm start                              # ng serve (dev)
npm run build                          # production build -> dist/sensor-app
npm test                               # Karma + Jasmine (needs a test target)
npx eslint .                           # lint
```

---

## 2. Code conventions

### 2.1 Git

- `main` is protected — never commit directly. Branch as `feat/<scope>`,
  `fix/<scope>`, `chore/<scope>`, `docs/<scope>`.
- Commits: `<type>(<scope>): <summary>` — types: feat, fix, chore, docs,
  refactor, test; imperative mood; subject under 80 chars.
- PRs are small and focused — one concern per PR; one approval + green CI
  before merge.
- Close issues explicitly, one keyword each: `Closes #a, closes #b`.
- Never force-push shared branches; merge `main` in when behind.
- After merge: delete the remote and local branch, then pull `main`.
- Never commit: `.env`, `instance/`, `*.db`, `__pycache__/`,
  `.mypy_cache/`, `node_modules/`, `dist/`, `.angular/`, `*.zip`,
  `package-lock.json` is **committed** (do not ignore it).
- Migrations are committed — never regenerate a migration already merged.

### 2.2 Python (backend)

- Target Python 3.12; type hints on every signature; `mypy --strict`
  clean (no bare `# type: ignore`).
- Lint and format with ruff + ruff format; code MUST pass natively, not
  via `--fix` as an afterthought.
- Names are documentation: verbs for functions, nouns for classes,
  `is`/`has`/`can` for booleans; no single-letter names (except loop
  counters / `e` in `except`).
- Cognitive complexity ≤ 15 per function; max nesting depth 3 — prefer
  early returns and guard clauses.
- No magic numbers/strings — name them as constants (e.g. the 10s sample
  interval, the 1–100 limit bounds).
- No debug statements (`print`, `pdb`), no commented-out code, no dead
  branches in committed code.

### 2.3 Application factory & configuration

- `create_app(config=None)` in `sensor_api/__init__.py` does ONLY wiring:
  config, extensions (`ext.init_app(app)`), blueprints, error handlers.
- Never use a global `app` outside `create_app`. Never start threads,
  generate data, or call `db.create_all()` inside the factory — schema
  comes from migrations.
- Three config classes: `DevelopmentConfig`, `TestingConfig`,
  `ProductionConfig`. `DEBUG`/`FLASK_DEBUG` MUST be `False` in production
  — the Werkzeug debugger must never ship in a container.
- All config from environment variables; no hardcoded secrets, no real
  values as defaults. Required vars documented in `.env.example`:
  `DATABASE_URL`, `SECRET_KEY`, `CORS_ORIGINS`.
- CORS is scoped to `CORS_ORIGINS` (the frontend origin) — never `*`.

### 2.4 Blueprints & API

- One blueprint per domain (`sensors`, `health`). Register with a URL
  prefix; version the API: `/api/v1/sensors`.
- Routes are thin: validate input → call a service → encode response. No
  business logic, no direct DB queries in handlers.
- Validate all input at the boundary with a schema; reject unknown/bad
  input with `400`. `?limit=` MUST be a bounded integer (1–100) and a
  non-integer MUST return `400`, never silently fall back to a default.
- Errors return JSON (RFC 9457-style), not Werkzeug HTML — register
  error handlers for the app's exception types and for `abort()`.
- Path segments lowercase, plural collection nouns, no trailing slash;
  query params for filter/sort/paginate only.

### 2.5 Database

- SQLAlchemy 2.x ORM — no raw SQL strings; `select()` style, no
  `SELECT *`.
- Schema changes ship a reversible Flask-Migrate (Alembic) migration —
  one per logical change, each with a working `down`. No
  `db.create_all()` at runtime.
- Index every column queried/ordered (e.g. `SensorData.timestamp`).
- Serialize timestamps as ISO-8601 UTC (`.isoformat()`), not RFC-1123.
- Wrap multi-step writes in a transaction; on failure roll back the
  session — never leave a poisoned session. Use the connection pool with
  explicit limits.

### 2.6 Background data generation

- The simulator runs as a **dedicated worker process**
  (`sensor_api/worker.py` / a CLI command), started as its own service —
  NOT a thread inside `create_app`. This avoids duplicate generators
  under multi-worker gunicorn and keeps the web process stateless.
- The worker owns its own app context and DB session; wrap each insert
  in try/except + rollback; log start/insert/error.
- Sample interval is a named, env-configurable constant (default 10s).

### 2.7 TypeScript / Angular (frontend)

- Angular 19 standalone components; `strict: true` and strict templates;
  no `any` — type the API boundary with the `SensorData` interface.
- Call the API via `HttpClient`, never `fetch`. Always handle errors
  with `catchError`; render explicit loading, empty, and error states —
  never a silent blank table.
- The API base URL comes from `environments/environment*.ts`, never
  hardcoded. Do not rely on `REACT_APP_*` vars (wrong framework).
- Load data in `ngOnInit` (or a resolver), not the constructor. For
  "real-time", poll with RxJS `interval()` (or SSE/WebSocket) and render
  via the `async` pipe.
- Format for humans with pipes (`| number:'1.1-2'`, `| date:'medium'`);
  give coded values (e.g. vibration 0/1) a legend.
- Accessibility per `frontend/ux.md` (WCAG 2.1 AA): table `<caption>` +
  `scope` on headers; decorative images use `alt=""` (not both `alt` and
  `aria-hidden`).
- No dead tutorial scaffolding, mock `db.json`, or unused deps in the
  app.

### 2.8 Observability & Grafana

- Structured JSON logs; default level INFO (no DEBUG in production);
  never log secrets or PII. Log each error once, at the top of the stack.
- `/health` = shallow liveness (200 if process alive, no auth);
  `/ready` = deep readiness (checks PostgreSQL, 503 if down).
- Grafana datasources and dashboards are provisioned from
  `deploy/grafana/provisioning/` (YAML + JSON) and version-controlled —
  no changes made only through the Grafana UI.

### 2.9 Containers & Compose

- Each service has a `.dockerignore`; never `COPY . .` without one.
- Multi-stage builds: backend runs gunicorn; frontend builds and is
  served by a pinned nginx (no `ng serve` in production).
- Pin base images (Python 3.12-slim, postgres:16, node:22-alpine,
  grafana pinned) — no floating `latest`.
- `docker-compose.yml`: every service has a `healthcheck` and a
  `restart` policy; `depends_on` uses `condition: service_healthy`. Do
  not expose the DB port to the host in production. Secrets via env, not
  literals.

---

## 3. Quality

### 3.1 Testing

- Backend: pytest + pytest-flask; one `app` fixture in `conftest.py`
  using `TestingConfig` against a real PostgreSQL test DB (no SQLite
  substitution). Test each route for success (2xx), validation (400),
  and not-found (404). Seed data **directly** — never `time.sleep` on the
  generator; tests must be deterministic, not timing-coupled.
- Test names: `test_<unit>_<state>_<expected>`.
- Frontend: Karma + Jasmine with a real `test` target in `angular.json`
  and a `test` script in `package.json`; test `SensorService`
  (HTTP + error path) and `HomeComponent`. The sole spec MUST pass — no
  stale assertions.
- Coverage measured both stacks; new code ≥ 90%, total MUST NOT regress
  and SHOULD stay ≥ 80%.
- Full framework: `base/core/testing.md`.

### 3.2 Quality gates & CI

- Layer 1 (editor): `.editorconfig`, format-on-save.
- Layer 2 (pre-commit): ruff, mypy, eslint, gitleaks via
  `.pre-commit-config.yaml`.
- Layer 3 (CI): GitHub Actions on every PR and push to `main` — backend
  (ruff + mypy + pytest), frontend (lint + build + test), gitleaks, and
  CodeQL; Dependabot for pip, npm, and Actions. No "allowed to fail"
  stages. Full framework: `base/workflow/quality-gates.md`,
  `platform/github.md`, `base/infra/cicd.md`.

### 3.3 Security

- No secrets in source or history; scope CORS; validate all input at the
  boundary; `DEBUG=False` and no dev server in any shipped image; HTTPS
  for any non-local deployment; least-privilege CI permissions
  (`contents: read`). Full framework: `base/security/security.md`,
  `base/security/devsecops.md`.

---

## 4. Identity

Minimal. The frontend is a functional dashboard; follow `frontend/ux.md`
for layout/accessibility. No formal brand system — keep styling
consistent and the table readable.

---

## 5. Review process

### 5.1 Code review

Review the diff against `main` in priority order (highest first), per
`base/core/review.md`:

1. **Security** — `DEBUG=False`, no dev server in images, CORS scoped,
   input validated, no secrets/PII in logs.
2. **Correctness** — routes thin / services own logic; no generator
   thread in the factory; transactions rolled back on failure; Angular
   error/empty states handled; no N+1.
3. **Clarity** — self-documenting names, single-purpose functions,
   complexity ≤ 15.
4. **Conventions** — ruff + mypy strict clean; eslint clean; ISO
   timestamps; API versioned; migrations reversible.

Confirm CI is green before merge.

### 5.2 Structure audit

- Run `pytest && mypy src/ --strict` (backend) and `npm run build &&
  npm test` (frontend) before every PR.
- Verify `.env.example` lists every required var; README documents
  commands and env.
- Verify each new route has success/400/404 tests; each schema change
  has a reversible migration.
- Run a full 360 (`base/workflow/360.md`) after a milestone or before a
  release; store at `docs/audits/YYYY-MM-DD-360.md`.

---

## 6. Session protocol

Follow `docs/solid-ai-templates/templates/base/workflow/scope.md` for the
scope guard and end-of-session audit.

### 6.1 Start of session

1. Read this `CLAUDE.md` and `README.md` before the first change.
2. Check the current branch — if not `main`, ask why before proceeding.
3. Check `git status`; if uncommitted changes exist, finish/ship the
   prior session before new work.
4. Prune merged branches (`git fetch --prune`).
5. Confirm the scope with the user; if ambiguous, ask for the specific
   deliverable.

### 6.2 During the session

- Flag when work grows beyond the agreed scope — do not silently absorb
  new requests.
- Finishing and committing current work takes priority over starting new
  work.
- Run the relevant tests/linters after each change — do not accumulate
  unverified changes.
- When a tool touches unrelated files, revert the drift and file it
  separately.

### 6.3 End of session

When the user signals end of session ("wrap up", "let's finish", "end
session", "close out", or similar), print the full checklist below and
execute each item sequentially. Mark each item done (with result) before
moving to the next. Do not batch, skip, or summarize — visible
sequential execution prevents missed steps.

1. Commits and push — all changes committed and pushed (via PR if
   branch-protected).
2. Close issues — close completed issues (verify auto-close worked).
3. Epic checklists — update if relevant.
4. Dev journal — add a session entry to `docs/dev-journal.md` (date,
   tool, key changes, PRs merged, issues closed/created).
5. ADRs — record architectural decisions in `docs/decisions/`.
6. Migrations — confirm every schema change has a reversible migration
   committed and applied.
7. CLAUDE.md — for each new convention, decide if it belongs here (a rule
   the agent MUST apply every turn) or another doc; one line per rule.
8. README.md — confirm new commands/deps/env vars are reflected; name the
   section.
9. docs/ONBOARDING.md — confirm new tools/prerequisites/steps documented.
10. docs/PLAYBOOK.md — confirm new commands/scripts/workflows documented.
11. Tests and types — run backend and frontend test + type/lint gates;
    confirm all pass.
12. Flag gaps — report anything incomplete as pending (never as done).
13. Summary — summarize what was done and what is next.

<!-- Generated with solid-ai-templates (github.com/braboj/solid-ai-templates) -->
