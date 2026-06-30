import json
import unittest
from datetime import datetime

from sensor_api import create_app
from sensor_api.blueprints.sensors.models import SensorData
from sensor_api.extensions import db

SENSORS_URL = '/api/v1/sensors'


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

        response = self.client.get(SENSORS_URL)
        self.assertEqual(200, response.status_code)
        self.assertEqual(2, len(response.get_json()))

    def test_api_sensors_empty_returns_empty_list(self):
        """With no data the route returns 200 and an empty list."""
        response = self.client.get(SENSORS_URL)
        self.assertEqual(200, response.status_code)
        self.assertEqual([], response.get_json())

    def test_api_sensors_limit_caps_results(self):
        """The limit query parameter caps the number of rows returned."""
        db.session.add_all([_reading() for _ in range(3)])
        db.session.commit()

        response = self.client.get(f'{SENSORS_URL}?limit=1')
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.get_json()))

    def test_api_sensors_limit_out_of_range_returns_400(self):
        """A limit outside the 1-100 bounds is rejected with 400."""
        for test_val in (-1, 0, 101):
            response = self.client.get(f'{SENSORS_URL}?limit={test_val}')
            self.assertEqual(400, response.status_code)

    def test_api_sensors_non_integer_limit_returns_400(self):
        """A non-integer limit is rejected with 400, never coerced."""
        for test_val in ('abc', '1.5', ''):
            response = self.client.get(f'{SENSORS_URL}?limit={test_val}')
            self.assertEqual(400, response.status_code)

    def test_api_sensors_error_response_is_json_problem(self):
        """Errors are JSON (RFC 9457-style), not Werkzeug HTML."""
        response = self.client.get(f'{SENSORS_URL}?limit=abc')
        self.assertEqual(400, response.status_code)
        self.assertIn('application/problem+json', response.content_type)
        body = json.loads(response.get_data(as_text=True))
        self.assertEqual(400, body['status'])
        self.assertIn('detail', body)

    def test_api_sensors_timestamp_is_iso8601_utc(self):
        """Timestamps serialize as ISO-8601 UTC strings, not RFC-1123."""
        db.session.add(_reading())
        db.session.commit()

        response = self.client.get(SENSORS_URL)
        self.assertEqual(200, response.status_code)
        timestamp = response.get_json()[0]['timestamp']

        self.assertIsInstance(timestamp, str)
        parsed = datetime.fromisoformat(timestamp)
        self.assertIsNotNone(parsed.tzinfo)

    def test_api_sensors_stream_emits_latest_reading_as_sse(self):
        """The stream endpoint returns an SSE response priming the latest row.

        Only the first event is read; the stream is otherwise infinite, so the
        response is consumed unbuffered and closed rather than drained.
        """
        db.session.add(_reading(temperature=21.5))
        db.session.commit()

        response = self.client.get(f'{SENSORS_URL}/stream', buffered=False)
        try:
            self.assertEqual(200, response.status_code)
            self.assertIn('text/event-stream', response.content_type)
            self.assertEqual('no', response.headers.get('X-Accel-Buffering'))

            first_event = next(response.response)
            if isinstance(first_event, bytes):
                first_event = first_event.decode('utf-8')

            self.assertTrue(first_event.startswith('data:'))
            self.assertIn('"temperature": 21.5', first_event)
        finally:
            response.close()
