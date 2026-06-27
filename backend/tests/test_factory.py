import unittest

from sensor_api import create_app

class TestAppFactory(unittest.TestCase):


    def test_config(self):

        config = {
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
        }

        self.assertTrue(create_app(config).testing)