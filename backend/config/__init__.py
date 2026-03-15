"""Configuration helpers for Legacy AI."""

DEFAULT_CONFIG = {
    "DATABASE_URI": "sqlite:///legacyai.db",
    "JWT_SECRET_KEY": "your-secret-key",
}


def get_config():
    """Return default configuration values."""
    return DEFAULT_CONFIG
