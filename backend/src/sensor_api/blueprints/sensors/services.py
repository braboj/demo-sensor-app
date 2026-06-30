# encoding: utf-8
from collections.abc import Sequence

from sqlalchemy import select

from ...extensions import db
from ...sensors import AnalogSensor, DiscreteSensor
from .models import SensorData
from .schemas import DEFAULT_LIMIT

# The simulated field sensors, in the order readings are recorded.
Sensors = tuple[AnalogSensor, AnalogSensor, DiscreteSensor]


class SensorService(object):
    """Service class for handling sensor data."""

    @staticmethod
    def build_sensors() -> Sensors:
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
    def record_reading(sensors: Sensors) -> SensorData:
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
    def fetch_data(limit: int = DEFAULT_LIMIT) -> Sequence[SensorData]:
        """Return the latest sensor readings (ORM rows), newest first.

        Serialization is the boundary's job (see schemas.serialize_reading).
        """
        statement = (
            select(SensorData)
            .order_by(SensorData.timestamp.desc())
            .limit(limit)
        )
        return db.session.execute(statement).scalars().all()
