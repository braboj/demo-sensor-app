# ADR-0001 — Data generator runs as a dedicated worker process

**Status:** Accepted (2026-06-27, PR #34, issue #15)

## Context
The sensor data generator ran as a daemon `threading.Thread` started inside
`create_app()`. That meant a generator per gunicorn worker (duplicate
inserts), a second one under the dev reloader, and a live generator during
tests — which also forced timing-coupled tests (`time.sleep(11)`). It shared
the global `db.session` with no rollback.

## Decision
Run the generator as its own process, `backend/worker.py`, started as a
separate compose service. It owns its app context and DB session, samples on
an env-configurable interval (`SAMPLE_INTERVAL_SECONDS`, default 10s), and
rolls back per failed insert. `create_app()` no longer starts threads.

## Consequences
- Exactly one generator regardless of web concurrency; the web process is
  stateless, so gunicorn can run multiple workers safely.
- Tests seed `SensorData` directly and are deterministic (suite ~22s → <1s).
- Trade-off: one more compose service to run.
- `db.create_all()` still runs in the factory until Alembic migrations land
  (#22); removing it is tracked there.
