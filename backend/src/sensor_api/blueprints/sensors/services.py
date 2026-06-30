# encoding: utf-8
from sqlalchemy import select

from ...extensions import db
from ...sensors import AnalogSensor, DiscreteSensor
from .models import SensorData
from .schemas import DEFAULT_LIMIT


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
        """Return the latest sensor readings (ORM rows), newest first.

        Serialization is the boundary's job (see schemas.serialize_reading).
        """
        statement = (
            select(SensorData)
            .order_by(SensorData.timestamp.desc())
            .limit(limit)
        )
        return db.session.execute(statement).scalars().all()

    @staticmethod
    def fetch_since(last_id, limit=DEFAULT_LIMIT):
        """Return readings newer than ``last_id`` (ORM rows), oldest first.

        Used by the live SSE stream to pull rows inserted since the last
        event was sent. Ordered ascending by id so events arrive in the
        order they were recorded and the caller can advance its cursor to
        the final row's id.
        """
        statement = (
            select(SensorData)
            .where(SensorData.id > last_id)
            .order_by(SensorData.id.asc())
            .limit(limit)
        )
        return db.session.execute(statement).scalars().all()
