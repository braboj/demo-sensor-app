from flask import Flask
from flask_cors import CORS

from .blueprints.health import health
from .blueprints.sensors import api
from .config import get_config, split_origins
from .errors import register_error_handlers
from .extensions import db, migrate


def create_app(test_config=None):
    """Application factory — wiring only (config, extensions, blueprints).

    No global app, no threads, no db.create_all(): the schema comes from
    Alembic migrations and the data generator runs as a separate worker
    process (``python -m sensor_api.worker``).
    """

    app = Flask(__name__, instance_relative_config=True)

    # Load the environment-selected config class (defaults to the safe
    # ProductionConfig); an explicit mapping from the tests overrides it.
    app.config.from_object(get_config())
    if test_config is not None:
        app.config.from_mapping(test_config)

    # Scope CORS to the configured frontend origins — never a wildcard.
    origins = split_origins(app.config.get('CORS_ORIGINS'))
    CORS(app, resources={r"/api/*": {"origins": origins}})

    # Register the domain blueprints.
    app.register_blueprint(api)
    app.register_blueprint(health)

    # Render errors as JSON (RFC 9457-style), not Werkzeug HTML.
    register_error_handlers(app)

    # Initialise the database and migration engine against the app.
    db.init_app(app)
    migrate.init_app(app, db)

    return app
