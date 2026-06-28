"""Sensor data generator.

The canonical deployment runs this as its own process — NOT a thread inside
``create_app`` — so there is exactly one generator regardless of how many
gunicorn workers serve the API, and none runs during tests or under the dev
reloader. It owns its own app context and DB session, and rolls back on a
failed insert.

Run locally:   python -m sensor_api.worker
In compose:    command: ["python", "-m", "sensor_api.worker"]

The generation loop is also reusable as ``run_generator``: hosting tiers with
no background worker (e.g. Render free) start it in-process inside the gunicorn
request worker via ``gunicorn.conf.py`` — a documented exception to the
separate-worker rule (CLAUDE.md 2.6), gated behind ``RUN_INPROCESS_GENERATOR``.
"""
import logging
import os
import time

from flask import Flask

from sensor_api import create_app
from sensor_api.blueprints.sensors.services import SensorService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
log = logging.getLogger("sensor.worker")

# Sample interval in seconds — env-configurable, defaults to 10s.
SAMPLE_INTERVAL_SECONDS = int(os.getenv("SAMPLE_INTERVAL_SECONDS", "10"))


def run_generator(app: Flask | None = None) -> None:
    """Generate and persist a sensor reading every sample interval.

    Loops forever. Accepts an existing ``app`` (the in-process hook may pass
    one); otherwise it builds its own via the factory. Owns its app context for
    the lifetime of the loop and never lets one failed insert stop the loop.
    """
    app = app or create_app()
    sensors = SensorService.build_sensors()
    log.info("sensor generator started; interval=%ss", SAMPLE_INTERVAL_SECONDS)

    with app.app_context():
        while True:
            try:
                reading = SensorService.record_reading(sensors)
                log.info("recorded sensor reading id=%s", reading.id)
            except Exception:
                log.exception("failed to record sensor reading")
            time.sleep(SAMPLE_INTERVAL_SECONDS)


def run() -> None:
    """Entry point for the standalone worker process."""
    run_generator()


if __name__ == "__main__":
    run()
