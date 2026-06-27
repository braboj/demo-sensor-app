import unittest
from backend.app import create_app
from backend.app.database import db
from backend.app.models import SensorData


def _reading(temperature=20.0, humidity=50.0, vibration=0):
    """Build a SensorData row for seeding tests directly."""
    return SensorData(
        temperature=temperature, humidity=humidity, vibration=vibration
    )


class FlaskRouteTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Run once before all tests."""

        config = {
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
        }

        cls.app = create_app(test_config=config)
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.create_all()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests."""
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

    def setUp(self):
        """Run before each test."""
        self.client = self.app.test_client()
        self.app.testing = True

    def tearDown(self):
        """Run after each test."""
        db.session.remove()
        db.drop_all()
        db.create_all()

    def test_index_route(self):
        """Test the index route."""
        response = self.client.get('/')
        self.assertEqual(200, response.status_code)

    def test_404_route(self):
        """Test the 404 route."""
        response = self.client.get('/notfound')
        self.assertEqual(404, response.status_code)

    def test_api_sensors_returns_seeded_rows(self):
        """All seeded readings are returned by default."""
        db.session.add_all([_reading(), _reading(vibration=1)])
        db.session.commit()

        response = self.client.get('/api/sensors')
        self.assertEqual(200, response.status_code)
        self.assertEqual(2, len(response.get_json()))

    def test_api_sensors_empty_returns_empty_list(self):
        """With no data the route returns 200 and an empty list."""
        response = self.client.get('/api/sensors')
        self.assertEqual(200, response.status_code)
        self.assertEqual([], response.get_json())

    def test_api_sensors_limit_caps_results(self):
        """The limit query parameter caps the number of rows returned."""
        db.session.add_all([_reading() for _ in range(3)])
        db.session.commit()

        response = self.client.get('/api/sensors?limit=1')
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.get_json()))

    def test_api_sensors_limit_out_of_range_returns_400(self):
        """A limit outside the 1-100 bounds is rejected with 400."""
        for test_val in (-1, 0, 101):
            response = self.client.get(f'/api/sensors?limit={test_val}')
            self.assertEqual(400, response.status_code)
