# 4. Solution Strategy

This chapter summarizes the fundamental decisions that shape the architecture.
Each maps to a quality goal or a constraint, cited by ID (e.g. QG02, T03) rather
than restated here. The significant decisions are recorded in full as ADRs and
indexed in [Chapter 9](09-architecture-decisions.md).

## 4.1 Technology decisions

| Decision | Rationale |
| --- | --- |
| A Flask application assembled by an application factory, with blueprints per domain (sensors, health). | Keeps wiring in one place and routes thin; no global app, so tests build their own (T01). |
| SQLAlchemy 2.x ORM with Alembic migrations; no schema created at runtime. | The schema is a reviewed, reversible artifact rather than a side effect of startup (T03). |
| PostgreSQL as the single system of record, with the `timestamp` column indexed. | The dominant query is "newest N readings"; the index keeps it cheap (QG01, QG04). |
| gunicorn with a cooperative `gevent` worker as the production server. | A long-lived stream connection must not tie up a worker; a cooperative worker serves many open streams (QG02, S01). |
| Server-Sent Events for live delivery. | New readings flow one way, server to browser; SSE rides plain HTTP and reconnects natively, without the weight of WebSockets (FR05, and ADR-0005). |
| An Angular single-page application built once and served static by nginx, which reverse-proxies `/api` to the backend. | One origin means no CORS in the browser path, and the SPA is a set of cacheable static files (S03, and ADR-0003). |
| Grafana provisioned as code and embedded in the page. | Charts get a mature tool without building a charting layer; provisioning keeps the datasource and dashboard in version control (FR07, and ADR-0007/0008). |

## 4.2 Approaches to functional requirements

| Requirement | Approach |
| --- | --- |
| FR01 | A dedicated worker samples three simulated sensors — two analog (temperature, humidity), one discrete (vibration 0/1) — every `SAMPLE_INTERVAL_SECONDS` (default 10). |
| FR02 | Each sample becomes one `sensor_data` row; the database stamps the record time by default. |
| FR03 | A versioned `GET /api/v1/sensors` blueprint returns readings as a JSON array, newest first. |
| FR04 | `parse_limit()` bounds `?limit=` to 1–100 and rejects a non-integer or out-of-range value with a 400 — never a silent fallback. |
| FR05 | `GET /api/v1/sensors/stream` holds the connection open and pushes each newly recorded row as an SSE event. |
| FR06 | The web page loads a snapshot on init, then subscribes to the stream, and renders explicit loading, empty, error, and live states. |
| FR07 | A Grafana "Sensor Readings" dashboard, provisioned from YAML/JSON, is embedded on the Charts tab. |
| FR08 | `GET /health` reports process liveness; `GET /ready` runs `SELECT 1` and returns 503 when the database is unreachable. |

## 4.3 Approaches to key quality goals

| Quality goal | Strategy |
|--------------|----------|
| QG01 Correctness | One ordered, limited query returns readings newest-first; timestamps are serialized as ISO-8601 UTC; the `?limit=` bound is enforced at the boundary. |
| QG02 Reliability | Each write is a commit-or-rollback so a failure never poisons the session; the worker loop survives a bad insert; the cooperative server keeps open streams from blocking other requests. |
| QG03 Maintainability | `src` layout, factory + blueprints, a domain layer that knows nothing about Flask, typed signatures, `ruff` + `mypy --strict`, and coverage gates enforced in CI across both stacks. |
| QG04 Portability | Every service is a pinned image; the same images run under local Compose and on the hosted platform, which injects the port and the database URL. |
| QG05 Observability | A shallow `/health` and a deep `/ready` answer different operational questions; the worker logs start, each insert, and each failure. |
| QG06 Usability | A one-command local stack, a live table with human-formatted values and a legend, an embedded dashboard, and a hosted demo let an evaluator explore in minutes. The table is accessible. |
| QG07 Security | No secrets in the repo (all config via environment, scanned in CI); CORS scoped to the frontend origin; debug off and gunicorn/nginx — never a dev server — in every image. |

## 4.4 Organizational decisions

- A single `pyproject.toml` configures the backend package, its dependencies,
  and the `ruff` / `mypy` / `pytest` toolchain; the frontend is configured
  through `package.json` and `angular.json`.
- Work happens on branches through pull requests into a protected `main`, gated
  by CI (lint, type-check, tests, secret scan, and CodeQL) before merge (O01,
  O03).
- Architecture decisions are captured as ADRs under `docs/decisions/`, indexed
  from [Chapter 9](09-architecture-decisions.md).
- arc42 (this documentation) is the architecture reference.
