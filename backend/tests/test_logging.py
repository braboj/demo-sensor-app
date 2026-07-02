"""Tests for structured JSON logging (logging_config)."""
import json
import logging
import sys

from sensor_api.logging_config import JsonFormatter, configure_logging


def _record(msg: str, *args: object, level: int = logging.INFO) -> logging.LogRecord:
    return logging.LogRecord(
        name="sensor.test",
        level=level,
        pathname=__file__,
        lineno=1,
        msg=msg,
        args=args,
        exc_info=None,
    )


def test_jsonformatter_emits_core_fields() -> None:
    payload = json.loads(JsonFormatter().format(_record("hello %s", "world")))
    assert payload["level"] == "INFO"
    assert payload["logger"] == "sensor.test"
    assert payload["message"] == "hello world"
    assert payload["time"].endswith("Z")


def test_jsonformatter_surfaces_extra_fields() -> None:
    record = _record("recorded")
    record.reading_id = 42
    payload = json.loads(JsonFormatter().format(record))
    assert payload["reading_id"] == 42


def test_jsonformatter_includes_exception_traceback() -> None:
    try:
        raise ValueError("boom")
    except ValueError:
        record = _record("failed", level=logging.ERROR)
        record.exc_info = sys.exc_info()
    payload = json.loads(JsonFormatter().format(record))
    assert "ValueError: boom" in payload["exc_info"]


def test_configure_logging_installs_single_json_handler() -> None:
    root = logging.getLogger()
    saved_handlers, saved_level = root.handlers[:], root.level
    try:
        configure_logging("DEBUG")
        assert len(root.handlers) == 1
        assert isinstance(root.handlers[0].formatter, JsonFormatter)
        assert root.level == logging.DEBUG

        # Idempotent, and an unknown level falls back to INFO.
        configure_logging("NOPE")
        assert len(root.handlers) == 1
        assert root.level == logging.INFO
    finally:
        root.handlers, root.level = saved_handlers, saved_level
