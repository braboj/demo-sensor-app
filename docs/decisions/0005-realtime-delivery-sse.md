# ADR-0005 — Real-time delivery via Server-Sent Events (SSE)

**Status:** Accepted (2026-06-30, issue #8)

## Context
The dashboard showed near-real-time data by polling `GET /api/v1/sensors`
on an RxJS `interval()`. Issue #8 asked for push-based "real-time delivery"
so new readings appear without repeated full-list requests. The data flows
one way only (server → browser), the backend is a synchronous Flask app run
under gunicorn, and the deploy targets are Docker Compose and a Render free
tier — both resource-constrained.

The original codebase carried an unused `flask-socketio` dependency and a
dead WebSocket prototype under `backend/scripts/` (flagged by the 360 audit).

## Decision
Use **Server-Sent Events** rather than WebSockets:

- Backend: `GET /api/v1/sensors/stream` returns `text/event-stream`. A
  generator primes the connection with the latest reading, then polls the
  database every `STREAM_POLL_SECONDS` for rows newer than the last id sent
  and pushes each as a `data:` event (with `: keep-alive` heartbeats in
  between).
- Run gunicorn with the **gevent** worker class (`GUNICORN_WORKER_CLASS`,
  default `gevent`) so a long-lived stream does not tie up the single web
  worker. gevent monkey-patches at worker start, so the free-tier in-process
  generator's daemon thread cooperates instead of blocking.
- nginx gets a dedicated unbuffered `location` for the stream
  (`proxy_buffering off`, HTTP/1.1, long read timeout); the backend also
  sends `X-Accel-Buffering: no` so Render's proxy flushes events too.
- Frontend: `SensorService.streamReadings()` wraps `EventSource` in an
  Observable; `HomeComponent` loads the initial snapshot over HTTP, then
  prepends streamed readings (deduped by id, capped) and shows a live /
  live-error status.
- Remove the unused `flask-socketio` dependency and the dead WebSocket
  prototype.

## Consequences
- Unidirectional push fits the data; SSE is plain HTTP, needs no extra
  client library, auto-reconnects, and rides the existing same-origin proxy
  (ADR-0003) with no new CORS surface.
- The stream is DB-poll-backed, not event-driven; new rows surface within
  `STREAM_POLL_SECONDS`. A pub/sub (e.g. Postgres `LISTEN/NOTIFY`) would
  remove the poll but adds infrastructure not warranted at this scale.
- gevent + psycopg2 is not fully cooperative (libpq blocks the hub during a
  query); query times are sub-millisecond at this scale, so it is acceptable.
  `psycogreen` is the upgrade path if contention appears.
- WebSockets remain available as a future option if bidirectional needs
  (commands, acks) arise; this decision does not preclude them.
