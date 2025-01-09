import hashlib
from typing import Any
from dotenv import load_dotenv
import os
import bcrypt
import jwt
import datetime
import boto3


def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def hash_email(email: str) -> str:
    return hashlib.sha256(email.encode('utf-8')).hexdigest()

def create_jwt(user_email: str) -> str:
    payload = {
        'user_id': user_email,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
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

def upload_file_to_s3(file_name:str, bucket_name:str, object_name:str) -> bool:
    try:
        s3_client.upload_file(file_name, bucket_name, object_name)
        return True
    except:
        return False

def download_file_from_s3(object_name:str, download_path:str) -> bool:
    try:
        s3_client.download_file(BUCKET_NAME, object_name, download_path)
        return True
    except:
        return False

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY', 'DEFAULT_KEY')
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY', 'DEFAULT_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY', 'DEFAULT_SECRET_KEY')
BUCKET_NAME = os.getenv('S3_BUCKET','DEFAULT_BUCKET')
s3_client = boto3.client(
    's3',
    aws_access_key_id = AWS_ACCESS_KEY,
    aws_secret_access_key = AWS_SECRET_KEY
)





