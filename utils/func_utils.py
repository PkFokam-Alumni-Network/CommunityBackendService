import boto3
import hashlib
import os
import bcrypt
import jwt
import datetime
from typing import Any
from core.logging_config import LOGGER
from utils.image_utils import crop_image_to_circle, decode_base64_image
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email
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


def verify_jwt(token: str) -> Any | None:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")

def upload_file_to_s3(file_data: bytes, object_key: str) -> str:
    
    try:
        s3_client.put_object(
            Bucket=settings.BUCKET_NAME,
            Body=file_data,
            Key=object_key,
        )
        LOGGER.info(
            f"File uploaded to S3 bucket '{settings.BUCKET_NAME}' with key '{object_key}'."
        )
        return f"https://{settings.BUCKET_NAME}.s3.us-east-2.amazonaws.com/{object_key}"
    except Exception as e:
        LOGGER.error(f"Error uploading file to key {object_key}: {e}")
        raise ValueError("Error uploading file to S3 bucket")

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


def reset_password_email(email: str, token: str, name: str):
    link = f"{settings.BASE_URL}/password-reset?token={token}"
    base_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(base_dir, "templates", "password_reset_email.html")
    template_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "templates",
        "password_reset.html",
    )
    with open(template_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    html_content = html_content.replace("{{name}}", name)
    html_content = html_content.replace("{link}", link)

    message = Mail(
        from_email=Email(settings.ADMIN_EMAIL, name="PACI SUPPORT"),
        to_emails=email,
        subject="Password Reset",
        html_content=html_content,
    )
    sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
    try:
        response = sg.send(message)
        LOGGER.info(f"Password reset link sent to {email}.")
        return response.status_code
    except Exception as e:
        LOGGER.error(f"Error sending password reset email to {email}: {e}")
        raise ValueError("Error sending password reset email")
