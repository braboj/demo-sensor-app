from .models import SensorData
from .database import db
from .sensors import AnalogSensor, DiscreteSensor


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
    def fetch_data(limit=100):
        """Get the latest sensor data from the database."""

        # Get the required amount of sensor readings
        data = SensorData.query.order_by(
            SensorData.timestamp.desc()
        ).limit(limit).all()

        # Return the data in json format
        return [
            {
                "id": entry.id,
                "timestamp": entry.timestamp,
                "temperature": entry.temperature,
                "humidity": entry.humidity,
                "vibration": entry.vibration
            } for entry in data
        ]
