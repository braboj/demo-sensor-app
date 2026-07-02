# 8. Crosscutting Concepts

Concepts that apply across multiple building blocks.

## 8.1 Sensor model (domain)

A sensor is a named source that produces one value on demand. Two kinds cover the
demo: an **analog** sensor draws a floating-point value within a range (used for
temperature and humidity), and a **discrete** sensor draws an integer within a
range (used for vibration, bounded to 0/1). Each is constructed with a tag and
its limits, validates those limits, and yields a value from `read()`. The worker
builds the three sensors once and reads all three to form one reading.

| Concept | Implementation |
| --- | --- |
| Analog reading | `AnalogSensor` — a float in `[low, high]` (default 0.0–100.0) |
| Discrete reading | `DiscreteSensor` — an integer in `[low, high]` (default 0–1) |
| One reading | `SensorService.record_reading()` reads all three and persists a row |

## 8.2 Statelessness of the web tier

The backend keeps no mutable state between requests. Each request opens a
database session, does its work, and returns; nothing is cached in the process
that a later request depends on. This is what lets the web tier scale by adding
workers or replicas, and it keeps the request path independent of the generator,
which runs on its own schedule. The one deliberate exception is the free-tier
in-process generator ([Chapter 7](07-deployment-view.md)), which is a background
thread, not request state.

## 8.3 Configuration

All configuration comes from environment variables; nothing environment-specific
is hardcoded, and no real secret has a default. One of three config classes is
selected by `APP_CONFIG`, and the debugger is off outside development.

| Concept | Implementation |
| --- | --- |
| Config classes | `DevelopmentConfig`, `TestingConfig`, `ProductionConfig` (default), chosen by `APP_CONFIG` |
| Database URL | `DATABASE_URL`; a legacy `postgres://` prefix is normalized to `postgresql://` |
| Scoped CORS | `CORS_ORIGINS` (comma-separated) applied to `/api/*`; empty means deny |
| Secrets | `SECRET_KEY` and the database URL come from the environment; none are committed |

The full variable surface — including the worker interval, the server port and
worker count, and the frontend build variables — is documented in
`backend/.env.example` and the [README configuration table](../../README.md).

## 8.4 Persistence and schema

Readings live in one table, `sensor_data`, defined by a typed SQLAlchemy 2.x
model and created only through migrations — never at runtime. The `timestamp`
column carries a database default and is indexed, because the dominant read is
"the newest N ordered by time". Reads use `select()` with an explicit order and
limit, not raw SQL.

| Concept | Implementation |
| --- | --- |
| Model | `SensorData` — `id`, `timestamp` (indexed, DB default), `temperature`, `humidity`, `vibration` |
| Schema delivery | Alembic migration `dd76030f5961`; `flask db upgrade` on startup, no `db.create_all()` |
| Time format | serialized as ISO-8601 UTC (`+00:00`) at the boundary, not a locale format |
| Write safety | `record_reading()` commits, and rolls back on failure so the session is never poisoned |

## 8.5 Input validation

Input is validated at the boundary before any query runs. The `?limit=` query
parameter must be an integer within 1–100; a non-integer or out-of-range value
is rejected with a 400 rather than silently clamped or defaulted. Absent, it
defaults to 100.

| Concept | Implementation |
| --- | --- |
| Bounds | `MIN_LIMIT = 1`, `MAX_LIMIT = 100`, `DEFAULT_LIMIT = 100` |
| Enforcement | `parse_limit()` in `schemas.py`; a bad value aborts with 400 |

## 8.6 Error handling (the JSON error contract)

Errors return one uniform JSON shape, never a Werkzeug HTML page. Registered
handlers turn Flask/Werkzeug `HTTPException`s and the application's own
`BackendError` into an RFC 9457 `application/problem+json` body. An unexpected
failure is logged in full but answered with a generic message, so internal detail
never reaches the client.

| Exception | Status | Body (`application/problem+json`) |
| --- | --- | --- |
| `HTTPException` (e.g. a 400 from `parse_limit`, an unknown path → 404) | `exc.code` | `{title, status, detail}` from the exception |
| `BackendError` / any other exception | 500 | `{title, status, detail}` with a generic detail; the cause is logged |

The base exception is `BackendError` in
[`errors.py`](../../backend/src/sensor_api/errors.py); the handlers are
registered by the application factory.

## 8.7 Real-time delivery

Live updates use Server-Sent Events: a one-way, server-to-browser channel over
plain HTTP that the browser's `EventSource` reconnects on its own. The stream is
cursor-based — it remembers the id of the last row it sent and asks only for rows
after it — so it never re-sends or misses a reading. A keep-alive comment every
couple of seconds holds the connection open through proxies.

| Concept | Implementation |
| --- | --- |
| Endpoint | `GET /api/v1/sensors/stream` → `text/event-stream` |
| Cursor | `SensorService.fetch_since(last_id)`; poll interval `STREAM_POLL_SECONDS = 2.0` |
| Proxy handling | nginx exact-match location with `proxy_buffering off` and a long read timeout |
| Server | a cooperative `gevent` gunicorn worker, so an open stream doesn't block others |

## 8.8 Observability

Logs are structured JSON lines on stdout, for the container runtime to collect.
The worker logs each meaningful step — start, each recorded reading, and any
failure (with a traceback); debug logging is never on in production. Operators
have two probes for two questions: `GET /health` answers "is the process alive?"
without touching any dependency, and `GET /ready` answers "can it serve?" by
running `SELECT 1` and returning 503 when the database is unreachable.

| Aspect | Implementation |
| --- | --- |
| Log format | structured JSON to stdout, via the formatter in `logging_config.py`, applied by the application factory |
| Log level | env-driven (`LOG_LEVEL`), default INFO; no DEBUG in production |
| Liveness | `GET /health` → `200 {"status":"ok"}`, no dependencies |
| Readiness | `GET /ready` → `200 {"status":"ready"}` or `503 {"status":"unavailable"}` (DB probe) |

## 8.9 Security

The demo has no authentication and stores no user data, so its security rests on
a small attack surface and clean configuration rather than an auth layer, which
is out of scope. Secrets stay out of the repository and are scanned for in CI;
CORS is scoped to the frontend origin; the debugger is off and only gunicorn and
nginx — never a dev server — run in the images.

| Aspect | Implementation |
| --- | --- |
| Secrets | none in the repo; gitleaks scans in CI and pre-commit; `SECRET_KEY` generated per deploy on the host |
| CORS | scoped to `CORS_ORIGINS`; never a wildcard |
| Debug / server | debug off; gunicorn (backend) and nginx (frontend) in every image |
| Container user | both images run as a non-root user; the backend is a multi-stage build |
| Grafana | anonymous read-only viewer on the hosted demo; embedding enabled deliberately because the instance is read-only (ADR-0008) |
| Transport | services speak plain HTTP; the platform edge terminates TLS |

## 8.10 Frontend UX and accessibility

The web page never shows a silent blank screen: every state is rendered
explicitly — a loading message, an error alert if the snapshot fails, an empty
notice when there are no readings, a live indicator while the stream is flowing,
and a fallback alert if the stream drops. Values are formatted for humans, and
the coded vibration value is given a legend.

| Concept | Implementation |
| --- | --- |
| Explicit states | `loading`, `error`, empty, `live`, and `liveError`, each with `role="status"`/`role="alert"` |
| Human formatting | `date:'medium'`; `number:'1.1-2'` with units; `vibration` mapped to "None"/"Detected" |
| Accessible table | a `<caption>` carrying the vibration legend, and `scope="col"` on every header |
| Bounded growth | the always-open stream caps the visible rows so the table cannot grow without bound |

## 8.11 Build, tooling, and testing

Each stack is built and checked through a declarative toolchain, and CI runs the
same checks on every push and pull request. The backend uses one `pyproject.toml`
for the package, its dependencies, and the `ruff` / `mypy` / `pytest` config; the
frontend uses `package.json` and `angular.json`. Pre-commit hooks mirror the CI
checks locally.

| Tool | Role |
| --- | --- |
| `ruff` + `mypy --strict` | backend lint/format and strict typing (no bare `# type: ignore`) |
| `pytest` | backend tests against a real database, seeded directly (never timing-coupled to the generator) |
| ESLint + Prettier | frontend lint and formatting |
| Karma + Jasmine | frontend unit tests (`SensorService` and the home view) |
| gitleaks + CodeQL | secret scanning and static analysis, in CI (and gitleaks in pre-commit) |

See [Chapter 2](02-architecture-constraints.md) for the binding constraints and
[Chapter 10](10-quality-requirements.md) for the quality scenarios these tools
enforce.
