import random
from abc import ABC, abstractmethod

from .errors import BackendError


class _SensorAbc(ABC):
    """Abstract class for sensors."""

    @property
    @abstractmethod
    def tag(self):
        """The tag name of the sensor.

        Returns:
            str: The tag name of the sensor.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def low_limit(self):
        """The low limit of the sensor.

        Returns:
            int | float: The low limit of the sensor.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def high_limit(self):
        """The high limit of the sensor.

        Returns:
            int | float: The high limit of the sensor.
        """
        raise NotImplementedError

    @abstractmethod
    def read(self):
        """Read the sensor data.

        Returns:
            int | float: The sensor data.
        """
        raise NotImplementedError

    @abstractmethod
    def validate(self):
        """Validate the sensor instance."""
        raise NotImplementedError


class _SensorBase(object):
    """Base class for all sensors types."""

    def __init__(self, tag, low_limit, high_limit):
        """Initialize the sensor with a tag name."""

        self._tag = tag
        self._low_limit = low_limit
        self._high_limit = high_limit
        self._last_value = None

    def __str__(self):
        return f"{self.tag}: {self._last_value}"

    def __repr__(self):
        return str(self)

    @property
    def tag(self):
        """The tag name of the sensor."""
        return self._tag

    @property
    def low_limit(self):
        """The low limit of the sensor."""
        return self._low_limit

    @property
    def high_limit(self):
        """The high limit of the sensor."""
        return self._high_limit

    def validate(self):
        """Validate the discrete sensor instance."""

        # Validate the sensor instance
        if not isinstance(self.tag, str):
            raise BackendError(
                message=f"The tag name {self.tag} must be a string",
                context=f"Expected {str}, got {type(self.tag)}"
            )

        # Validate low limit type
        if not isinstance(self.low_limit, (float, int)):
            raise BackendError(
                message=f"Low limit {self.low_limit} must be a numeric value",
                context=f"Expected {float}, got {self.low_limit}"
            )

        # Validate high limit type
        if not isinstance(self.high_limit, (float, int)):
            raise BackendError(
                message=f"High limit {self.high_limit} must be a numeric value",
                context=f"Expected {float}, got {self.high_limit}"
            )

        # Validate the order of the limits
        if self.low_limit > self.high_limit:
            raise BackendError(
                message="The low limit must be less than the high limit",
                context=f"Low limit: {self.low_limit}, High limit: {self.high_limit}"
            )

        return self


class DiscreteSensor(_SensorBase, _SensorAbc):
    """Generates random integer data for discrete sensors.

    Example:

        # Position sensor (-1: down, 0: stop, 1: up)
        sensor1 = DiscreteSensor('ZSS1R01A', low_limit=-1, high_limit=1)
        sensor1.read()

        # Vibration sensor (0: off, 1: on)
        sensor2 = DiscreteSensor('VSS1R01A', low_limit=0, high_limit=1)
        sensor2.read()
    """

    def __init__(self, tag, low_limit=0, high_limit=1):

        # Call the base class constructor
        super(DiscreteSensor, self).__init__(tag, low_limit, high_limit)

        # Validate the sensor instance
        self.validate()

        # Convert the limits to integers
        self._low_limit = int(self.low_limit)
        self._high_limit = int(self.high_limit)

    def read(self):
        """Read the discrete sensor data."""

        self._last_value = random.randint(self.low_limit, self.high_limit)
        return self._last_value

    def validate(self):
        """Validate the discrete sensor instance."""

        # Validate the basic requirements for the sensor
        super().validate()

        # Validate the specific requirements for the low limits
        if not isinstance(self.low_limit, int):
            raise BackendError(
                message=f"Low limit {self.low_limit} must be an integer value",
                context=f"Expected {int}, got {self.low_limit}"
            )

        # Validate the specific requirements for the high limits
        if not isinstance(self.high_limit, int):
            raise BackendError(
                message=f"High limit {self.high_limit} must be an integer value",
                context=f"Expected {int}, got {self.high_limit}"
            )

        # Return the validated sensor instance
        return self


class AnalogSensor(_SensorBase, _SensorAbc):
    """Generates random float data for analog sensors.

    Example:

        # Temperature sensor with a range of 0-100 degrees
        sensor1 = AnalogSensor('TIS1P01A', low_limit=0, high_limit=100)
        sensor1.read()

        # Pressure sensor with a range of 0-10 bar
        sensor2 = AnalogSensor('PIS1P01A', low_limit=0, high_limit=10)
        sensor2.read()
    """

    def __init__(self, tag, low_limit=0.0, high_limit=100.0):

        # Call the base class constructor
        super(AnalogSensor, self).__init__(tag, low_limit, high_limit)

        # Validate the sensor instance
        self.validate()

        # Convert the limits to float
        self._low_limit = float(self.low_limit)
        self._high_limit = float(self.high_limit)

    def read(self):
        """Read the analog sensor data."""

        self._last_value = random.uniform(self.low_limit, self.high_limit)
        return self._last_value

    def validate(self):

        # Validate the basic requirements for the sensor
        super().validate()

        # Validate the specific requirements for the low limits
        if not isinstance(self.low_limit, float):
            raise BackendError(
                message=f"Low limit {self.low_limit} must be a float value",
                context=f"Expected {float}, got {self.low_limit}"
            )

        # Validate the specific requirements for the high limits
        if not isinstance(self.high_limit, float):
            raise BackendError(
                message=f"High limit {self.high_limit} must be a float value",
                context=f"Expected {float}, got {self.high_limit}"
            )

        # Return the validated sensor instance
        return self


__all__ = ['DiscreteSensor', 'AnalogSensor']
