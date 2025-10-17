import boto3
import hashlib
import bcrypt
import jwt
import datetime
from typing import Any
from core.logging_config import LOGGER
from utils.image_utils import crop_image_to_circle, decode_base64_image
from core.settings import settings


s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.ACCESS_KEY,
    aws_secret_access_key=settings.SECRET_KEY,
)


def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def hash_email(email: str) -> str:
    return hashlib.sha256(email.encode("utf-8")).hexdigest()


def create_jwt(user_email: str) -> str:
    time_zone = datetime.timezone(datetime.timedelta(hours=5))
    payload = {
        "user_id": user_email,
        "exp": datetime.datetime.now(tz=time_zone) + datetime.timedelta(hours=1),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return token

def decode_jwt(token: str) -> Any | None:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")

def verify_jwt(token: str) -> Any | None:
    return decode_jwt(token)

def upload_image_to_s3(base64_image: str, object_key: str) -> str:
    image = decode_base64_image(base64_image)
    image = crop_image_to_circle(image)
    try:
        s3_client.put_object(
            Bucket=settings.BUCKET_NAME,
            Body=image,
            ContentType="image/jpeg",
            Key=object_key,
        )
        LOGGER.info(
            f"File uploaded to S3 bucket '{settings.BUCKET_NAME}' with key '{object_key}'."
        )
        return f"https://{settings.BUCKET_NAME}.s3.us-east-1.amazonaws.com/{object_key}"
    except Exception as e:
        LOGGER.error(f"Error uploading file to key {object_key}: {e}")
        raise ValueError("Error uploading file to S3 bucket")