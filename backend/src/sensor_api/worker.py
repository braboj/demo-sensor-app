"""Standalone sensor data generator.

Runs as its own process — NOT a thread inside ``create_app`` — so there is
exactly one generator regardless of how many gunicorn workers serve the
API, and none runs during tests or under the dev reloader. It owns its own
app context and DB session, and rolls back on a failed insert.

Run locally:   python -m sensor_api.worker
In compose:    command: ["python", "-m", "sensor_api.worker"]
"""
import logging
import os
import time

from sensor_api import create_app
from sensor_api.blueprints.sensors.services import SensorService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
log = logging.getLogger("sensor.worker")

# Sample interval in seconds — env-configurable, defaults to 10s.
SAMPLE_INTERVAL_SECONDS = int(os.getenv("SAMPLE_INTERVAL_SECONDS", "10"))


def run() -> None:
    """Generate and persist a sensor reading every sample interval."""
    app = create_app()
    sensors = SensorService.build_sensors()
    log.info("sensor worker started; interval=%ss", SAMPLE_INTERVAL_SECONDS)

    with app.app_context():
        while True:
            try:
                reading = SensorService.record_reading(sensors)
                log.info("recorded sensor reading id=%s", reading.id)
            except Exception:
                log.exception("failed to record sensor reading")
            time.sleep(SAMPLE_INTERVAL_SECONDS)


if __name__ == "__main__":
    run()
