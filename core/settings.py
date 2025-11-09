import boto3
import json
import os


class Settings:
    def __init__(self):
        self.ENV = os.getenv("ENV", "development")

        if self.ENV == "production":
            # secrets = self._load_production_secrets() will fix when Adlaelaelu fix secrets manager
            secrets = self._load_dev_secrets()
        else:
            secrets = self._load_dev_secrets()

        self._set_common_attributes(secrets)

    def _load_production_secrets(self):
        secret_name = os.getenv("SECRETS_MANAGER_NAME", "creds")
        region_name = os.getenv("AWS_REGION", "us-east-1")

        client = boto3.client("secretsmanager", region_name=region_name)
        secret_value = client.get_secret_value(SecretId=secret_name)
        return json.loads(secret_value["SecretString"])

    def _load_dev_secrets(self):
        return {
            "SECRET_KEY": os.getenv("SECRET_KEY", "DEFAULT_KEY"),
            "ACCESS_KEY": os.getenv("ACCESS_KEY", "DEFAULT_KEY"),
            "BUCKET_NAME": os.getenv("BUCKET_NAME", "DEFAULT_BUCKET"),
            "ADMIN_EMAIL": os.getenv("ADMIN_EMAIL"),
            "SENDGRID_API_KEY": os.getenv("SENDGRID_API_KEY"),
            "BASE_URL": os.getenv("BASE_URL"),
            "DOCS_AUTH_USERNAME": os.getenv("DOCS_AUTH_USERNAME"),
            "DOCS_AUTH_PASSWORD": os.getenv("DOCS_AUTH_PASSWORD"),
            "DATABASE_URL": os.getenv("DATABASE_URL"),
        }

    def _set_common_attributes(self, secrets: dict):
        self.SECRET_KEY = secrets.get("SECRET_KEY", "DEFAULT_KEY")
        self.ACCESS_KEY = secrets.get("ACCESS_KEY", "DEFAULT_KEY")
        self.BUCKET_NAME = secrets.get("BUCKET_NAME", "DEFAULT_BUCKET")
        self.ADMIN_EMAIL = secrets.get("ADMIN_EMAIL")
        self.SENDGRID_API_KEY = secrets.get("SENDGRID_API_KEY")
        self.BASE_URL = secrets.get("BASE_URL")
        self.DATABASE_URL = secrets.get("DATABASE_URL")
        self.DOCS_AUTH_USERNAME = secrets.get("DOCS_AUTH_USERNAME")
        self.DOCS_AUTH_PASSWORD = secrets.get("DOCS_AUTH_PASSWORD")


    @property
    def cors_origins(self):
        if self.ENV != "production":
            return ["http://localhost:5173", "http://127.0.0.1:5173"]
        return [
            "https://pkfalumni.com",
            "https://backoffice.pkfalumni.com",
            "https://staging.pkfalumni.com",
        ]

settings = Settings()