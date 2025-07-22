import os
import boto3
import json
from dotenv import load_dotenv
load_dotenv()


class Settings:
    def __init__(self):
        self.ENV = os.getenv("ENV", "development")

        if self.ENV == "production":
            secret_name = os.getenv("SECRETS_MANAGER_NAME", "paci/backend/creds")
            region_name = os.getenv("AWS_REGION", "us-east-1")

            client = boto3.client("secretsmanager", region_name=region_name)
            secret_value = client.get_secret_value(SecretId=secret_name)
            secrets = json.loads(secret_value["SecretString"])

            self.SECRET_KEY = secrets.get("SECRET_KEY", "DEFAULT_KEY")
            self.ACCESS_KEY = secrets.get("ACCESS_KEY", "DEFAULT_KEY")
            self.BUCKET_NAME = secrets.get("BUCKET_NAME", "DEFAULT_BUCKET")
            self.ADMIN_EMAIL = secrets.get("ADMIN_EMAIL")
            self.SENDGRID_API_KEY = secrets.get("SENDGRID_API_KEY")
            self.BASE_URL = secrets.get("BASE_URL")
            self.DATABASE_URL = secrets.get("DATABASE_URL")
            self.DOCS_AUTH_USERNAME = secrets.get("DOCS_AUTH_USERNAME")
            self.DOCS_AUTH_PASSWORD = secrets.get("DOCS_AUTH_PASSWORD")
        else:
            self.SECRET_KEY = os.getenv("SECRET_KEY", "DEFAULT_KEY")
            self.ACCESS_KEY = os.getenv("ACCESS_KEY", "DEFAULT_KEY")
            self.BUCKET_NAME = os.getenv("BUCKET_NAME", "DEFAULT_BUCKET")
            self.ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
            self.SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
            self.BASE_URL = os.getenv("BASE_URL")
            self.DATABASE_URL = os.getenv("DATABASE_URL")
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
            return self.DATABASE_URL

settings = Settings()
