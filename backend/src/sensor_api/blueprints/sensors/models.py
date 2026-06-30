# encoding: utf-8
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from ...extensions import Base


class SensorData(Base):
    """Basic sensor data model with temperature, humidity, and vibration.

    The model is deliberately kept simple for demonstration purposes. In a real
    application, the model would likely include additional fields, such as
    sensor ID, location, and metadata.
    """

    __tablename__ = "sensor_data"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Indexed: every read orders by timestamp DESC (see SensorService). Nullable
    # to match the committed migration; the DB default always populates it.
    timestamp: Mapped[datetime | None] = mapped_column(
        default=func.current_timestamp(), index=True
    )
    temperature: Mapped[float] = mapped_column(nullable=False)
    humidity: Mapped[float] = mapped_column(nullable=False)
    vibration: Mapped[int] = mapped_column(nullable=False)

    def __repr__(self) -> str:
        return f"<SensorData id={self.id} timestamp={self.timestamp}>"
