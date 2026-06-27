import unittest
from sensor_api.sensors import AnalogSensor, DiscreteSensor

class TestDiscreteSensor(unittest.TestCase):


    def setUp(self):
        """Fixture that runs before each test method."""

        # Create a default discrete sensor
        self.sensor = DiscreteSensor('ZSS1R01A', low_limit=-1, high_limit=1)


    def test_default_init(self):
        """Test the default initialization of the discrete sensor."""

        sensor = DiscreteSensor('AAAA')

        self.assertEqual(sensor.tag, 'AAAA')
        self.assertEqual(sensor.low_limit, 0)
        self.assertEqual(sensor.high_limit, 1)

    def test_custom_init(self):
        """Test the custom initialization of the discrete sensor."""

        sensor = DiscreteSensor('BBBB', low_limit=-2, high_limit=2)

        self.assertEqual(sensor.tag, 'BBBB')
        self.assertEqual(sensor.low_limit, -2)
        self.assertEqual(sensor.high_limit, 2)

    def test_tag(self):
        """Test the tag property of the discrete sensor."""

        self.assertEqual(self.sensor.tag, 'ZSS1R01A')

        with self.assertRaises(AttributeError):
            self.sensor.tag = 'AAAA' # noqa

    def test_low_limit(self):

        self.assertEqual(self.sensor.low_limit, -1)

        with self.assertRaises(AttributeError):
            self.sensor.low_limit = -2 # noqa

    def test_high_limit(self):

        self.assertEqual(self.sensor.high_limit, 1)

        with self.assertRaises(AttributeError):
            self.sensor.high_limit = 2 # noqa

    def test_read(self):

        for i in range(1000):
            value = self.sensor.read()
            self.assertTrue(-1 <= value <= 1)
            self.assertTrue(isinstance(value, int))

    def test_validate(self):

        # Test the low limit
        for test_value in ('A', 1j, [1, 2, 3], {'A': 1}):
            with self.assertRaises(Exception):
                DiscreteSensor('AAAA', low_limit=test_value, high_limit=1)

        # # Test the high limit type
        # self.sensor.low_limit = -1      # noqa
        # self.sensor.high_limit = 'A'    # noqa
        # with self.assertRaises(Exception):
        #     self.sensor.validate()
        #
        # # Test the low limit order
        # self.sensor.high_limit = -2     # noqa
        # with self.assertRaises(Exception):
        #     self.sensor.validate()


class TestAnalogSensor(unittest.TestCase):

    def setUp(self):
        """Fixture that runs before each test method."""

        # Create a default discrete sensor
        self.sensor = AnalogSensor('TIS1R01A', low_limit=-100.0, high_limit=100.0)


    def test_default_init(self):
        """Test the default initialization of the discrete sensor."""

        sensor = AnalogSensor('AAAA')

        self.assertEqual(sensor.tag, 'AAAA')
        self.assertEqual(sensor.low_limit, 0.0)
        self.assertEqual(sensor.high_limit, 100.0)

    def test_custom_init(self):
        """Test the custom initialization of the discrete sensor."""

        sensor = AnalogSensor('BBBB', low_limit=-200.0, high_limit=200.0)

        self.assertEqual(sensor.tag, 'BBBB')
        self.assertEqual(sensor.low_limit, -200.0)
        self.assertEqual(sensor.high_limit, 200.0)

    def test_tag(self):
        """Test the tag property of the discrete sensor."""

        self.assertEqual(self.sensor.tag, 'TIS1R01A')

        with self.assertRaises(AttributeError):
            self.sensor.tag = 'AAAA' # noqa

    def test_low_limit(self):

        # Test the read access
        self.assertIsInstance(self.sensor.low_limit, float)

        # Test the write access
        with self.assertRaises(AttributeError):
            self.sensor.low_limit = -2 # noqa

    def test_high_limit(self):

        self.assertIsInstance(self.sensor.low_limit, float)

        with self.assertRaises(AttributeError):
            self.sensor.high_limit = 2 # noqa

    def test_read(self):

        for i in range(1000):
            value = self.sensor.read()
            self.assertTrue(-100.0 <= value <= 100.0)
            self.assertTrue(isinstance(value, float))

if __name__ == '__main__':
    unittest.main()
