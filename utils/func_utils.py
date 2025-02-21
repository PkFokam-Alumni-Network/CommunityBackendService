import boto3, hashlib, os, bcrypt, jwt, datetime, logging

from typing import Any
from dotenv import load_dotenv

from utils.image_utils import crop_image_to_circle, decode_base64_image

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    handlers=[
        logging.StreamHandler() 
    ]
)

logger = logging.getLogger(__name__)
load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY', 'DEFAULT_KEY')
ACCESS_KEY = os.getenv('ACCESS_KEY','DEFAULT_KEY')
BUCKET_NAME = os.getenv('BUCKET_NAME','DEFAULT_BUCKET')
s3_client = boto3.client(
    's3',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY
)

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

def upload_image_to_s3(base64_image: str, object_name:str) -> str:
    image = decode_base64_image(base64_image)
    image = crop_image_to_circle(image)
    object_key = f"profile-pictures/{object_name}"
    try:
        s3_client.put_object(
            Bucket = BUCKET_NAME,
            Body = image,
            ContentType = 'image/jpeg',
            Key = object_key)
        logger.info(f"File uploaded to S3 bucket '{BUCKET_NAME}' with key '{object_key}'.")
        return f"https://{BUCKET_NAME}.s3.us-east-2.amazonaws.com/profile-pictures/{object_key}"
    except Exception as e:
        logger.error(f"Error uploading file as {object_name}: {e}")
        raise ValueError("Error uploading file to S3 bucket")


    







