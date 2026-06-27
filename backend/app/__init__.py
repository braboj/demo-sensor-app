import threading
from flask import Flask
from flask_cors import CORS
from .config import get_config, split_origins
from .routes import api, main
from .database import db
from .services import SensorService

def create_app(test_config=None):

    app = Flask(__name__, instance_relative_config=True)

    # Load the environment-selected config class (defaults to the safe
    # ProductionConfig); an explicit mapping from the tests overrides it.
    app.config.from_object(get_config())
    if test_config is not None:
        app.config.from_mapping(test_config)

    # Scope CORS to the configured frontend origins — never a wildcard.
    origins = split_origins(app.config.get('CORS_ORIGINS'))
    CORS(app, resources={r"/api/*": {"origins": origins}})

    # Register the routes with the app
    app.register_blueprint(main)
    app.register_blueprint(api)

    # Initialize the database
    db.init_app(app)

    # Create the database tables
    with app.app_context():
        db.create_all()

    # Start the sensor data generation thread
    with app.app_context():
        sensor_thread = threading.Thread(
            target=SensorService.generate_data,
            args=(app,)
        )
        sensor_thread.daemon = True
        sensor_thread.start()

    return app