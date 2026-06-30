# encoding: utf-8
"""Request validation and response serialization for the sensors API.

Keeps the route thin: the boundary parses/validates the query and shapes
the response here, the service owns the query.
"""
from datetime import datetime, timezone
from typing import Any

from flask import abort

from .models import SensorData

# Bounds for the ?limit= query parameter (inclusive). A missing value uses
# the default; a non-integer or out-of-range value is rejected with 400.
DEFAULT_LIMIT = 100
MIN_LIMIT = 1
MAX_LIMIT = 100


def parse_limit(raw: str | None) -> int:
    """Validate the ?limit= query value into a bounded integer.

    Returns ``DEFAULT_LIMIT`` when absent; aborts with ``400`` on a
    non-integer or out-of-range value — never silently coerced.
    """
    if raw is None:
        return DEFAULT_LIMIT

    try:
        limit = int(raw)
    except (TypeError, ValueError):
        abort(400, description="The 'limit' parameter must be an integer")

    if limit < MIN_LIMIT or limit > MAX_LIMIT:
        abort(
            400,
            description=(
                f"The 'limit' parameter must be between "
                f"{MIN_LIMIT} and {MAX_LIMIT}"
            ),
        )

    return limit


def _iso_utc(value: datetime | None) -> str | None:
    """Serialize a datetime as an ISO-8601 string in UTC.

    Stored timestamps are naive UTC (the DB ``current_timestamp`` default);
    they are tagged as UTC so the wire format is unambiguous (``+00:00``).
    """
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat()


def serialize_reading(row: SensorData) -> dict[str, Any]:
    """Shape one ``SensorData`` row into a JSON-ready dict."""
    return {
        "id": row.id,
        "timestamp": _iso_utc(row.timestamp),
        "temperature": row.temperature,
        "humidity": row.humidity,
        "vibration": row.vibration,
    }
