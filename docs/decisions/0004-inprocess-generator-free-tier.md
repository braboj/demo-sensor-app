# ADR-0004 — In-process data generator on the free hosting tier

**Status:** Accepted (2026-06-28, PR #55, issue #29)

## Context
[ADR-0001](0001-data-generator-as-worker-process.md) runs the sensor
generator as a dedicated process (`sensor_api.worker`), separate from the web
process. Render's free tier offers no background worker/cron service — only the
single web instance — so there is nowhere to run that separate process.

## Decision
Keep the dedicated worker as the canonical architecture. For the free tier
only, run the same generation loop in-process. The loop is extracted as
`worker.run_generator()` and started once from the gunicorn `post_worker_init`
hook (`backend/gunicorn.conf.py`) as a daemon thread, gated behind
`RUN_INPROCESS_GENERATOR`. The Blueprint sets `WEB_CONCURRENCY=1`, so there is
exactly one web worker and therefore exactly one generator.

It starts in the **worker, not the gunicorn master**: a thread started in the
master (`when_ready`) is still running when gunicorn forks the workers, and the
children inherit locks held mid-operation by that thread and deadlock — the
fork-after-thread hazard. The worker is a leaf process, so no fork happens after
the thread starts. (This failure was observed and fixed during PR #55: the
master variant wedged every request worker while data kept flowing.)

## Consequences
- The free-tier deploy needs no separate service; one web instance serves the
  API and generates data.
- The exception is opt-in and off by default — compose and any paid tier keep
  the separate worker (`RUN_INPROCESS_GENERATOR` unset), so ADR-0001 stands as
  the default.
- Correctness depends on a single web worker (`WEB_CONCURRENCY=1`); with more
  workers there would be one generator each. If the worker is replaced, the new
  one restarts the generator (self-healing).
- On a paid tier, drop `RUN_INPROCESS_GENERATOR` and add a worker service —
  tracked by #15.
