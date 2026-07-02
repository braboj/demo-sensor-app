"""Structured JSON logging for the backend.

Both entry points that run application code — the gunicorn-served web app and
the standalone generator worker — go through ``create_app``, which calls
``configure_logging`` so every log line is a single JSON object on stdout for
the container runtime to collect.

The level is env-driven (``LOG_LEVEL``, default INFO); DEBUG is never on by
default. Secrets and PII are never logged — only operational facts (ids,
levels, messages) and, on failure, the traceback.
"""
import json
import logging
import os
import sys
import time
from typing import Any

DEFAULT_LEVEL = "INFO"

# The attributes the stdlib sets on every LogRecord. Anything a caller attaches
# via ``logger.info(..., extra={...})`` is absent here, so we surface it as an
# extra top-level JSON field.
_STANDARD_ATTRS = frozenset(logging.makeLogRecord({}).__dict__) | {
    "message",
    "asctime",
    "taskName",
}


class JsonFormatter(logging.Formatter):
    """Render a log record as a single-line JSON object, timestamped in UTC."""

    converter = time.gmtime
    default_time_format = "%Y-%m-%dT%H:%M:%S"
    default_msec_format = "%s.%03dZ"

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "time": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key, value in record.__dict__.items():
            if key not in _STANDARD_ATTRS and not key.startswith("_"):
                payload[key] = value
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def configure_logging(level: str | None = None) -> None:
    """Install the JSON formatter as the sole root-logger handler.

    Idempotent: repeated calls leave exactly one JSON handler, so building the
    app more than once in a process never double-logs. An unknown level name
    falls back to INFO rather than raising.
    """
    resolved = (level or os.getenv("LOG_LEVEL", DEFAULT_LEVEL)).upper()
    # Map the name to its numeric level; an unknown name falls back to INFO.
    named_level = getattr(logging, resolved, None)
    level_value = named_level if isinstance(named_level, int) else logging.INFO

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level_value)
