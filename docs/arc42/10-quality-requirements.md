# 10. Quality Requirements

This chapter refines the quality goals from
[Chapter 1](01-introduction-and-goals.md) into a quality tree and concrete,
testable scenarios.

## 10.1 Quality tree

| Quality attribute | Refinement |
|-------------------|------------|
| Correctness | Readings stored and returned faithfully; newest-first ordering; bounded query; ISO-8601 UTC timestamps. |
| Reliability | Predictable failure on bad input; a write never poisons the session; the generator loop survives a failed insert. |
| Maintainability | Clear decomposition; lint/type gates on both stacks; coverage gates. |
| Portability | The same images run under local Compose and on the hosted platform. |
| Observability | Distinct liveness and readiness probes; the generator logs its work. |
| Usability | One-command stack; explicit UI states; human-formatted values; an accessible table. |
| Security | No secrets; scoped CORS; debug off; no dev server in any image. |

## 10.2 Quality scenarios

### Correctness

- **Q1 — Newest first, bounded.** `GET /api/v1/sensors` returns readings ordered
  newest-first; `?limit=n` returns at most `n`. *Verified by:*
  `backend/tests/test_routes.py`.
- **Q2 — Stable time format.** Every serialized reading carries an ISO-8601 UTC
  timestamp (`+00:00`), regardless of server locale. *Verified by:*
  `backend/tests/test_routes.py`.
- **Q3 — Faithful round-trip.** A directly seeded reading is returned with the
  same field values and the coded `vibration` intact. *Verified by:*
  `backend/tests/test_routes.py`, `backend/tests/test_sensors.py`.

### Reliability / robustness

- **Q4 — Predictable bad input.** `?limit=abc`, `?limit=0`, or `?limit=101`
  returns HTTP 400 with an `application/problem+json` body — never a silent
  default and never a 500. *Verified by:* `backend/tests/test_routes.py`.
- **Q5 — Unknown path is a clean 404.** An unmapped route returns a 404 problem
  document, not a Werkzeug HTML page. *Verified by:*
  `backend/tests/test_routes.py`.
- **Q6 — Write safety.** `record_reading()` commits, and rolls back on failure so
  the session is reusable; the worker loop logs and continues past a failed
  insert. *Verified by:* `backend/tests/test_sensors.py` and the
  [worker design](../decisions/0001-data-generator-as-worker-process.md).

### Observability

- **Q7 — Liveness vs. readiness.** `GET /health` returns 200 whenever the process
  is up; `GET /ready` returns 200 when the database is reachable and 503 when it
  is not. *Verified by:* `backend/tests/test_health.py`.

### Maintainability

- **Q8 — Gates green.** `ruff check`, `mypy --strict`, and `pytest` pass on the
  backend; ESLint, Prettier, `ng build`, and Karma pass on the frontend.
  *Enforced by:* [`ci.yml`](../../.github/workflows/ci.yml).
- **Q9 — Thin handlers.** Route handlers hold no business logic; the domain layer
  stays Flask-independent (which is what lets the worker reuse it). *Kept by:* the
  [Chapter 5](05-building-block-view.md) decomposition and code review.
- **Q10 — Config isolation.** The app builds under each config class, and
  production has debug off. *Verified by:* `backend/tests/test_config.py`,
  `backend/tests/test_factory.py`.

### Portability / usability / security

- **Q11 — Runs anywhere.** `docker compose up` brings up the full stack; the same
  images deploy on the hosted platform via [`render.yaml`](../../render.yaml).
- **Q12 — No silent blank screen.** The web page renders an explicit loading,
  empty, error, live, or live-error state for every condition. *Verified by:* the
  frontend `HomeComponent` and `SensorService` specs.
- **Q13 — No secrets, scoped CORS.** The repository holds no secrets (gitleaks in
  CI and pre-commit), and cross-origin access is limited to the configured
  frontend origin. *Verified by:* the CI secret scan and
  `backend/tests/test_config.py`.
