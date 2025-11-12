import os
import pytest
from core.settings import Settings


@pytest.fixture(autouse=True)
def clear_env_vars():
    """Clear relevant environment variables before each test and restore them afterwards."""
    env_vars = [
        "ENV",
        "SECRET_KEY",
        "ACCESS_KEY",
        "BUCKET_NAME",
        "ADMIN_EMAIL",
        "SENDGRID_API_KEY",
        "BASE_URL",
        "DOCS_AUTH_USERNAME",
        "DOCS_AUTH_PASSWORD",
    ]
    old_env = {var: os.environ.get(var) for var in env_vars}
    for var in env_vars:
        os.environ.pop(var, None)
    yield
    for var, val in old_env.items():
        if val is not None:
            os.environ[var] = val


def assert_default_settings(s: Settings):
    assert s.ENV == "development"
    assert s.SECRET_KEY == "DEFAULT_KEY"
    assert s.ACCESS_KEY == "DEFAULT_KEY"
    assert s.BUCKET_NAME == "DEFAULT_BUCKET"
    assert s.ADMIN_EMAIL is None
    assert s.SENDGRID_API_KEY is None
    assert s.BASE_URL is None
    assert s.DOCS_AUTH_USERNAME is None
    assert s.DOCS_AUTH_PASSWORD is None
    assert s.cors_origins == ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3001", "http://127.0.0.1:3001"]


def test_settings_defaults_without_env_vars():
    """Test default settings when no environment variables are set."""
    s = Settings()
    assert_default_settings(s)