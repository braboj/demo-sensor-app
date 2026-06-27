import unittest
from unittest.mock import patch

from backend.app import create_app
from backend.app.database import db


class HealthEndpointTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
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
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

    def setUp(self):
        self.client = self.app.test_client()

    def test_health_liveness_returns_200(self):
        """Liveness is shallow: 200 regardless of dependencies."""
        response = self.client.get('/health')
        self.assertEqual(200, response.status_code)
        self.assertEqual('ok', response.get_json()['status'])

    def test_ready_returns_200_when_database_reachable(self):
        """Readiness is 200 when the database answers."""
        response = self.client.get('/ready')
        self.assertEqual(200, response.status_code)
        self.assertEqual('ready', response.get_json()['status'])

    def test_ready_returns_503_when_database_unreachable(self):
        """Readiness is 503 when the database probe raises."""
        with patch.object(
            db.session, 'execute', side_effect=Exception('db down')
        ):
            response = self.client.get('/ready')
        self.assertEqual(503, response.status_code)
        self.assertEqual('unavailable', response.get_json()['status'])
