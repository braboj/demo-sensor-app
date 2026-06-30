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


def normalize_database_url(url: str) -> str:
    """Normalise a database URL for SQLAlchemy 2.x.

    Managed Postgres providers (e.g. Render) hand out URLs with the legacy
    ``postgres://`` scheme, which SQLAlchemy 2.x no longer recognises. Rewrite
    that prefix to ``postgresql://`` so the psycopg2 driver is selected. Every
    other scheme — including the ``postgresql+psycopg2://`` used by compose and
    the ``sqlite://`` used by tests — passes through unchanged.
    """
    legacy_prefix = "postgres://"
    if url.startswith(legacy_prefix):
        return "postgresql://" + url[len(legacy_prefix):]
    return url


class BaseConfig:
    """Settings shared across every environment."""

    SQLALCHEMY_DATABASE_URI = normalize_database_url(
        os.getenv("DATABASE_URL", "sqlite:///test.db")
    )
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
    selected = name or os.getenv("APP_CONFIG") or DEFAULT_CONFIG
    return CONFIG_MAP.get(selected, ProductionConfig)
