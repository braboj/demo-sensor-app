# encoding: utf-8
"""Server-Sent Events (SSE) stream for live sensor readings.

The data generator (the worker service, or the in-process loop on free tiers)
inserts a new row on a fixed interval. This stream polls the database for rows
newer than the last one sent and pushes each as an SSE ``data:`` event, so the
browser holds a single long-lived connection instead of repeatedly polling the
REST endpoint.

Requires a cooperative (gevent) gunicorn worker so a long-lived stream does not
tie up the single sync worker — see ``gunicorn.conf.py``.
"""
import json
import time
from collections.abc import Iterator

from flask import Flask

from .models import SensorData
from .schemas import serialize_reading
from .services import SensorService

# How often the stream checks the database for new readings. Kept well below
# the generator's sample interval (default 10s) so new rows surface promptly;
# named rather than a magic number.
STREAM_POLL_SECONDS = 2.0


def _format_event(payload: str) -> str:
    """Frame a JSON payload string as a single SSE ``data:`` event."""
    return f"data: {payload}\n\n"


def _serialize_event(row: SensorData) -> str:
    """Serialize one reading row into its SSE event string."""
    return _format_event(json.dumps(serialize_reading(row)))


def sensor_event_stream(app: Flask) -> Iterator[str]:
    """Yield SSE events for sensor readings as they are recorded.

    Sends the most recent reading immediately on connect, then streams each
    newly inserted row. ``app`` is the resolved application object (captured in
    the request handler) so the generator can open its own short-lived app
    context per poll — it outlives the request context and must not depend on
    it. Strings are built inside the context and yielded outside it, so no app
    context is held open while the generator is suspended at a ``yield``.
    """
    last_id = 0

    # Prime the connection: emit the latest reading right away (if any) so the
    # client renders immediately, then stream rows recorded after it.
    prime_event = None
    with app.app_context():
        latest = SensorService.fetch_data(limit=1)
        if latest:
            last_id = latest[0].id
            prime_event = _serialize_event(latest[0])
    if prime_event is not None:
        yield prime_event

    while True:
        with app.app_context():
            rows = SensorService.fetch_since(last_id)
            events = [_serialize_event(row) for row in rows]
            if rows:
                last_id = rows[-1].id

        if events:
            yield from events
        else:
            # A comment line doubles as a keep-alive heartbeat and lets the
            # server notice a client that has gone away.
            yield ": keep-alive\n\n"

        time.sleep(STREAM_POLL_SECONDS)
