import os
from pathlib import Path
import pytest
from settings import Settings

@pytest.fixture(autouse=True)
def clear_env_vars():
    """Clear relevant environment variables before each test and restore them afterwards."""
    env_vars = [
        "ENV", "SECRET_KEY", "ACCESS_KEY", "BUCKET_NAME", "ADMIN_EMAIL",
        "SENDGRID_API_KEY", "BASE_URL", "DOCS_AUTH_USERNAME", "DOCS_AUTH_PASSWORD"
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
    assert s.cors_origins == ["*"]
    assert s.database_url.startswith("sqlite:///")
    temp_file_path = s.database_url.replace("sqlite:///", "")
    assert temp_file_path.endswith(".db")
    assert Path(temp_file_path).exists()

def test_settings_defaults_without_env_vars():
    """Test default settings when no environment variables are set."""
    s = Settings()
    assert_default_settings(s)

def test_settings_with_production_env(monkeypatch):
    """Test settings when production environment variables are set."""
    monkeypatch.setenv("ENV", "production")
    monkeypatch.setenv("SECRET_KEY", "prod_secret")
    monkeypatch.setenv("ACCESS_KEY", "prod_access")
    monkeypatch.setenv("BUCKET_NAME", "prod_bucket")
    monkeypatch.setenv("ADMIN_EMAIL", "admin@prod.com")
    monkeypatch.setenv("SENDGRID_API_KEY", "sendgridkey")
    monkeypatch.setenv("BASE_URL", "https://prod.example.com")
    monkeypatch.setenv("DOCS_AUTH_USERNAME", "admin")
    monkeypatch.setenv("DOCS_AUTH_PASSWORD", "secret")
    monkeypatch.setenv("DATABASE_URL", "sqlite:////app/sql_database/database.db")

    s = Settings()
    assert s.ENV == "production"
    assert s.SECRET_KEY == "prod_secret"
    assert s.ACCESS_KEY == "prod_access"
    assert s.BUCKET_NAME == "prod_bucket"
    assert s.ADMIN_EMAIL == "admin@prod.com"
    assert s.SENDGRID_API_KEY == "sendgridkey"
    assert s.BASE_URL == "https://prod.example.com"
    assert s.DOCS_AUTH_USERNAME == "admin"
    assert s.DOCS_AUTH_PASSWORD == "secret"
    assert s.cors_origins == [
        "https://pkfalumni.com",
        "https://backoffice.pkfalumni.com"
    ]
    assert s.database_url == "sqlite:////app/sql_database/database.db"
