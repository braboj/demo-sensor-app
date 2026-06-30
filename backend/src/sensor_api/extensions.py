"""Shared Flask extension instances.

Defined module-level so models and blueprints can import them without a
circular dependency on the factory; bound to the app inside ``create_app``
via ``init_app``.
"""
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Typed declarative base.

    Giving SQLAlchemy an explicit ``DeclarativeBase`` lets models use
    ``Mapped[...]`` annotations, so instance attributes carry real types
    (e.g. ``SensorData.id`` is ``int``, not ``Any``) under ``mypy --strict``.
    """


db = SQLAlchemy(model_class=Base)
migrate = Migrate()
