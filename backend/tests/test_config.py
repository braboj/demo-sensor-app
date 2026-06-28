"""Tests for environment configuration helpers."""
from sensor_api.config import normalize_database_url


def test_normalize_database_url_legacy_postgres_scheme_rewritten():
    """A legacy ``postgres://`` URL is rewritten to ``postgresql://``."""
    url = "postgres://user:pass@host:5432/sensordb"
    assert normalize_database_url(url) == (
        "postgresql://user:pass@host:5432/sensordb"
    )


def test_normalize_database_url_postgresql_scheme_unchanged():
    """A modern ``postgresql://`` URL passes through untouched."""
    url = "postgresql://user:pass@host:5432/sensordb"
    assert normalize_database_url(url) == url


def test_normalize_database_url_psycopg2_driver_unchanged():
    """An explicit ``postgresql+psycopg2://`` URL (compose) is preserved."""
    url = "postgresql+psycopg2://postgres:postgres@db:5432/sensordb"
    assert normalize_database_url(url) == url


def test_normalize_database_url_sqlite_unchanged():
    """A non-Postgres scheme (tests use SQLite) is left as-is."""
    url = "sqlite:///:memory:"
    assert normalize_database_url(url) == url
