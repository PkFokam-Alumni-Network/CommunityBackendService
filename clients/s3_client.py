import boto3
from botocore.exceptions import ClientError
from core.logging_config import LOGGER
from core.settings import settings


class S3Client:
    def __init__(self, bucket_name: str = settings.BUCKET_NAME):
        self.bucket_name = bucket_name
        self.client = boto3.client(
            "s3",
            aws_access_key_id=settings.ACCESS_KEY,
            aws_secret_access_key=settings.SECRET_KEY,
        )

    def upload_file(self, file_bytes: bytes, object_key: str, content_type: str = "image/jpeg") -> str:
        try:
            self.client.put_object(
                Bucket=self.bucket_name,
                Body=file_bytes,
                ContentType=content_type,
                Key=object_key,
            )
            url = f"https://{self.bucket_name}.s3.us-east-1.amazonaws.com/{object_key}"
            LOGGER.info(f"File uploaded to S3 bucket '{self.bucket_name}' with key '{object_key}'.")
            return url
        except ClientError as e:
            LOGGER.error(f"Error uploading file to S3: {e}")
            raise ValueError("Error uploading file to S3 bucket")

    def delete_file(self, object_key: str) -> None:
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=object_key)
            LOGGER.info(f"File with key '{object_key}' deleted from S3 bucket '{self.bucket_name}'.")
        except ClientError as e:
            LOGGER.error(f"Error deleting file from S3: {e}")
            raise ValueError("Error deleting file from S3 bucket")

    def generate_file_url(self, object_key: str) -> str:
        return f"https://{self.bucket_name}.s3.us-east-1.amazonaws.com/{object_key}"
