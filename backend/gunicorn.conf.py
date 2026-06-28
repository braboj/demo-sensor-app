"""Gunicorn configuration for the sensor API.

Two jobs:

1. Bind the platform-provided ``$PORT`` (Render injects it) and read the worker
   count from ``WEB_CONCURRENCY``; both default to the compose-friendly values
   so the same image runs locally and in the cloud.

2. Optionally run the sensor data generator in-process. The canonical
   architecture runs the generator as its own service (``sensor_api.worker``),
   but free hosting tiers offer no background worker. When
   ``RUN_INPROCESS_GENERATOR`` is truthy we start the generation loop from the
   ``post_worker_init`` hook — i.e. inside the request worker, after it has
   forked — as a daemon thread.

   It must start in the worker, not the master: a thread started in the master
   (``when_ready``) would still be running when gunicorn forks the workers, and
   the children would inherit locks held mid-operation by that thread and
   deadlock (the fork-after-thread hazard). The worker is a leaf process, so no
   fork happens after the thread starts.

   This is a deliberate, documented exception to CLAUDE.md 2.6, scoped to the
   free tier and off by default (so compose/paid deploys keep the separate
   worker). It assumes a single web worker — the Blueprint sets
   ``WEB_CONCURRENCY=1`` — so there is exactly one generator; if the worker is
   replaced, the new one restarts it.
"""
import os
import threading

# Bind the platform port (Render sets $PORT); 5000 keeps compose/local intact.
bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"

# Request worker count. Free tier runs a single web instance; keep it at 1 so
# the in-process generator is the only one and resources stay within the free
# allowance. Override via WEB_CONCURRENCY on larger plans (and drop the
# in-process generator for a dedicated worker service there — see issue #15).
workers = int(os.getenv("WEB_CONCURRENCY", "1"))

_TRUTHY = {"1", "true", "yes", "on"}


def _is_enabled(value: str | None) -> bool:
    """Return True for the usual truthy string flags, False otherwise."""
    return value is not None and value.strip().lower() in _TRUTHY


def post_worker_init(worker: object) -> None:
    """Start the in-process generator once, inside the worker, when enabled.

    Runs only if ``RUN_INPROCESS_GENERATOR`` is set. The generator builds its
    own app context and DB session and loops on a daemon thread, so a single
    web worker (WEB_CONCURRENCY=1) means exactly one generator for the service.
    """
    if not _is_enabled(os.getenv("RUN_INPROCESS_GENERATOR")):
        return

    # Imported lazily so the worker only loads the generator when the in-process
    # mode is actually enabled.
    from sensor_api.worker import run_generator

    thread = threading.Thread(
        target=run_generator, name="sensor-generator", daemon=True
    )
    thread.start()
    worker.log.info("in-process sensor generator started (free-tier mode)")
