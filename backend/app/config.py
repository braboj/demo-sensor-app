"""Environment-specific Flask configuration.

Three config classes select behaviour by environment. The default is
``ProductionConfig`` so that a misconfigured deployment fails safe — the
Werkzeug debugger and dev server must never ship in a container.
"""
import os


def split_origins(raw: str | None) -> list[str]:
    """Parse a comma-separated CORS origin list into a clean list.

    An empty/unset value yields ``[]`` (deny all cross-origin) — never a
    wildcard.
    """
    if not raw:
        return []
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


class BaseConfig:
    """Settings shared across every environment."""

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///test.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY")
    # Comma-separated list of allowed frontend origins (see split_origins).
    CORS_ORIGINS = os.getenv("CORS_ORIGINS")


class DevelopmentConfig(BaseConfig):
    """Local development — the interactive debugger may be enabled."""

    DEBUG = True
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:4200")


class TestingConfig(BaseConfig):
    """Automated tests — disposable in-memory database, no debugger."""

    TESTING = True
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "TEST_DATABASE_URL", "sqlite:///:memory:"
    )


class ProductionConfig(BaseConfig):
    """Shipped containers — debugger and dev server forbidden."""

    DEBUG = False


CONFIG_MAP: dict[str, type[BaseConfig]] = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}

DEFAULT_CONFIG = "production"


def get_config(name: str | None = None) -> type[BaseConfig]:
    """Resolve a config class by name, defaulting to the safe production."""
    selected = name or os.getenv("APP_CONFIG", DEFAULT_CONFIG)
    return CONFIG_MAP.get(selected, ProductionConfig)
