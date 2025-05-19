import os

class Settings:
    ENV = os.getenv("ENV", "development")

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
        return "sqlite:////app/sql_database/database.db"

settings = Settings()