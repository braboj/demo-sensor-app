from datetime import timezone

from sqlalchemy import select

from .database import db
from .models import SensorData
from .sensors import AnalogSensor, DiscreteSensor

# Bounds for how many readings one query may return (inclusive). The API
# boundary validates ?limit= against these; the service default is used when
# no limit is supplied.
DEFAULT_LIMIT = 100
MIN_LIMIT = 1
MAX_LIMIT = 100


def _iso_utc(value):
    """Serialize a datetime as an ISO-8601 string in UTC.

    Stored timestamps are naive UTC (the DB ``current_timestamp`` default);
    they are tagged as UTC so the wire format is unambiguous (``+00:00``).
    """
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat()


class SensorService(object):
    """Service class for handling sensor data."""

    @staticmethod
    def build_sensors():
        """Construct the simulated field sensors.

        Built once by the worker and reused across samples so each sensor
        keeps its own state between readings.
        """
        return (
            AnalogSensor('temperature'),
            AnalogSensor('humidity'),
            DiscreteSensor('vibration'),
        )

    @staticmethod
    def record_reading(sensors):
        """Sample the sensors and persist a single reading.

        Requires an active app context. On failure the session is rolled
        back so it is never left poisoned, and the error is re-raised for
        the caller to log.
        """
        temperature, humidity, vibration = sensors
        reading = SensorData(
            temperature=temperature.read(),
            humidity=humidity.read(),
            vibration=vibration.read()
        )

        try:
            db.session.add(reading)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        return reading

    @staticmethod
    def fetch_data(limit=DEFAULT_LIMIT):
        """Get the latest sensor readings, newest first.

        Returns a list of plain dicts with the timestamp serialized as an
        ISO-8601 UTC string.
        """
        statement = (
            select(SensorData)
            .order_by(SensorData.timestamp.desc())
            .limit(limit)
        )
        rows = db.session.execute(statement).scalars().all()

        return [
            {
                "id": row.id,
                "timestamp": _iso_utc(row.timestamp),
                "temperature": row.temperature,
                "humidity": row.humidity,
                "vibration": row.vibration,
            }
            for row in rows
        ]
