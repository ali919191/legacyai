"""Configuration helpers for Legacy AI."""

from .database_config import DatabaseConfig, load_database_config

DEFAULT_CONFIG = {
    "DATABASE_URI": "sqlite:///legacyai.db",
    "JWT_SECRET_KEY": "your-secret-key",
}


def get_config():
    """Return default configuration values."""
    return DEFAULT_CONFIG


__all__ = [
    "DEFAULT_CONFIG",
    "get_config",
    "DatabaseConfig",
    "load_database_config",
]
