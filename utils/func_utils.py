import hashlib, os, bcrypt, jwt, datetime
from typing import Any
from dotenv import load_dotenv
from fastapi import UploadFile


def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def hash_email(email: str) -> str:
    return hashlib.sha256(email.encode('utf-8')).hexdigest()

def create_jwt(user_email: str) -> str:
    time_zone = datetime.timezone(datetime.timedelta(hours=5))
    payload = {
        'user_id': user_email,
        'exp': datetime.datetime.now(tz=time_zone) + datetime.timedelta(hours=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def verify_jwt(token: str) -> Any | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

MAX_FILE_SIZE = 5 * 1024 * 1024 # 5MB
def validate_image(image: UploadFile):
    allowed_types = ["image/jpeg", "image/png","image/jpg"]
    if image.content_type not in allowed_types:
        raise ValueError("Invalide file type. Only JPEG,JPG, PNG images are allowed")
    file_size = len(image.file.read())
    image.file.seek(0)
    if file_size > MAX_FILE_SIZE:
        raise ValueError("File is too large. Maximum size allowed is 5MB.")

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY', 'DEFAULT_KEY')
BUCKET_NAME = os.getenv('S3_BUCKET','DEFAULT_BUCKET')





