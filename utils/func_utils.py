import hashlib
from typing import Any
from dotenv import load_dotenv
import os
import bcrypt
import jwt
import datetime


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

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY', 'DEFAULT_KEY')
BUCKET_NAME = os.getenv('S3_BUCKET','DEFAULT_BUCKET')





