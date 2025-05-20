import os
import tempfile

class Settings:
    ENV = os.getenv("ENV", "development")
    SECRET_KEY = os.getenv("SECRET_KEY", "DEFAULT_KEY")
    ACCESS_KEY = os.getenv("ACCESS_KEY", "DEFAULT_KEY")
    BUCKET_NAME = os.getenv("BUCKET_NAME", "DEFAULT_BUCKET")
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')
    SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
    BASE_URL = os.getenv('BASE_URL')
    DOCS_AUTH_USERNAME = os.getenv("DOCS_AUTH_USERNAME")
    DOCS_AUTH_PASSWORD = os.getenv("DOCS_AUTH_PASSWORD")

    @property
    def cors_origins(self):
        if self.ENV == "development":
            return ["*"]  # Allow all origins for dev/testing
        return [
            "https://pkfalumni.com",
            "https://backoffice.pkfalumni.com"
        ]

    @property
    def database_url(self):
        if self.ENV == "development":
            # Create a temporary DB file per run (in-memory-like, but persisted for debug)
            temp_db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
            return f"sqlite:///{temp_db_file.name}"
        return "sqlite:////app/sql_database/database.db"

settings = Settings()