import os
import tempfile

class Settings:
    def __init__(self):
        self.ENV = os.getenv("ENV", "development")
        self.SECRET_KEY = os.getenv("SECRET_KEY", "DEFAULT_KEY")
        self.ACCESS_KEY = os.getenv("ACCESS_KEY", "DEFAULT_KEY")
        self.BUCKET_NAME = os.getenv("BUCKET_NAME", "DEFAULT_BUCKET")
        self.ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')
        self.ADMIN_NAME = os.getenv('ADMIN_NAME')
        self.BREVO_API_KEY = os.getenv('BREVO_API_KEY')
        self.SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
        self.BASE_URL = os.getenv('BASE_URL')
        self.DOCS_AUTH_USERNAME = os.getenv("DOCS_AUTH_USERNAME")
        self.DOCS_AUTH_PASSWORD = os.getenv("DOCS_AUTH_PASSWORD")


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
             return "sqlite:///database.db"
        else:
             return os.getenv("DATABASE_URL")

settings = Settings()