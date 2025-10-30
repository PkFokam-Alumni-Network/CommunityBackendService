import hashlib
import bcrypt
import jwt
import datetime
from typing import Any
from core.logging_config import LOGGER
from utils.image_utils import crop_image_to_circle, decode_base64_image
from core.settings import settings
from clients.s3_client import S3Client


s3_client = S3Client()

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
    
def validate_resume_file(file_data: bytes, file_name: str, max_size: int = 10 * 1024 * 1024) -> str:
    if not file_data:
        raise ValueError("Uploaded file is empty.")
    
    if not file_name:
        raise ValueError("File name is required.")
    
    if len(file_data) > max_size:
        max_mb = max_size / (1024 * 1024)
        raise ValueError(f"File size exceeds {max_mb}MB limit.")
    
    if not file_name.lower().endswith('.pdf'):
        raise ValueError("Only PDF files are allowed for resume uploads.")
    
    if not file_data.startswith(b'%PDF-'):
        raise ValueError("File does not appear to be a valid PDF format.")
    
    if b'%%EOF' not in file_data[-1024:]: 
        raise ValueError("File appears to be corrupted or incomplete PDF.")
    
def upload_file_to_s3(file_data: bytes, object_key: str) -> str:
    """
    Upload a file to S3 using the S3Client class.
    """
    try:
        from clients.s3_client import S3Client
        
        s3 = S3Client()
        url = s3.upload_file(
            file_bytes=file_data,
            object_key=object_key,
            content_type="application/pdf"  # For resume PDFs
        )
        
        LOGGER.info(f"File uploaded to S3 bucket with key '{object_key}'.")
        return url
        
    except Exception as e:
        LOGGER.error(f"Error uploading file to key {object_key}: {e}")
        raise ValueError("Error uploading file to S3 bucket")

def upload_image_to_s3(base64_image: str, object_key: str) -> str:
    image = decode_base64_image(base64_image)
    try:
        s3_client.upload_file(
            file_bytes=image,
            object_key=object_key,
            content_type="image/jpeg",
        )
        LOGGER.info(
            f"File uploaded to S3 bucket '{settings.BUCKET_NAME}' with key '{object_key}'."
        )
        return f"https://{settings.BUCKET_NAME}.s3.us-east-1.amazonaws.com/{object_key}"
    except Exception as e:
        LOGGER.error(f"Error uploading file to key {object_key}: {e}")
        raise ValueError("Error uploading file to S3 bucket")

def upload_profile_picture_to_s3(base64_image: str, object_key: str) -> str:
    image = decode_base64_image(base64_image)
    image = crop_image_to_circle(image)
    try:
        s3_client.upload_file(
            file_bytes=image,
            object_key=object_key,
            content_type="image/jpeg",
        )
        LOGGER.info(
            f"File uploaded to S3 bucket '{settings.BUCKET_NAME}' with key '{object_key}'."
        )
        return f"https://{settings.BUCKET_NAME}.s3.us-east-1.amazonaws.com/{object_key}"
    except Exception as e:
        LOGGER.error(f"Error uploading file to key {object_key}: {e}")
        raise ValueError("Error uploading file to S3 bucket")