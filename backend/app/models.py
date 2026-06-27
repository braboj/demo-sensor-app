# encoding: utf-8
from .database import db

class SensorData(db.Model):
    """Basic sensor data model with temperature, humidity, and vibration.

    The model is deliberately kept simple for demonstration purposes. In a real
    application, the model would likely include additional fields, such as
    sensor ID, location, and metadata.
    """

    id = db.Column(db.Integer, primary_key=True)
    # Indexed: every read orders by timestamp DESC (see SensorService).
    timestamp = db.Column(
        db.DateTime, default=db.func.current_timestamp(), index=True
    )
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)
    vibration = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<SensorData id={self.id} timestamp={self.timestamp}>"
