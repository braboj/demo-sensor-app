from flask import Flask
from flask_cors import CORS
from .config import get_config, split_origins
from .routes import api, main
from .database import db

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

    # Create the database tables. This stays until Alembic migrations land
    # (#22); the factory must otherwise do wiring only. The sensor data
    # generator runs as a separate worker process (worker.py), never a
    # thread spawned here.
    with app.app_context():
        db.create_all()

    return app