"""Shared Flask extension instances.

Defined module-level so models and blueprints can import them without a
circular dependency on the factory; bound to the app inside ``create_app``
via ``init_app``.
"""
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()
