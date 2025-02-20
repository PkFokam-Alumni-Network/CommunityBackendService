import base64, io, boto3, hashlib, os, bcrypt, jwt, datetime, logging
from PIL import Image
from typing import Any
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY', 'DEFAULT_KEY')
ACCESS_KEY = os.getenv('ACCESS_KEY','DEFAULT_KEY')
BUCKET_NAME = os.getenv('BUCKET_NAME','DEFAULT_BUCKET')
MAX_FILE_SIZE = 5 * 1024 * 1024 # 5MB
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

# the image received from the client is a base64 encoded string
def validate_image(base64_image: str) -> str:
    if base64_image.startswith('data:image'):
        base64_data = base64_image.split(",")[1]
    else:
        raise ValueError("Invalid base64 image format")

    try:
        image_data = base64.b64decode(base64_data)
    except Exception as e:
        raise ValueError(f"Error decoding base64 data: {str(e)}")

    image_file = io.BytesIO(image_data)
    
    try:
        with Image.open(image_file) as img:
            img_format = img.format.lower()
            allowed_formats = ["jpeg", "png", "jpg"]
            if img_format not in allowed_formats:
                raise ValueError("Invalid file type. Only JPEG, JPG, PNG images are allowed.")
            
            image_file.seek(0, io.SEEK_END)  
            file_size = image_file.tell()
            if file_size > MAX_FILE_SIZE:
                raise ValueError(f"File is too large. Maximum size allowed is {MAX_FILE_SIZE / (1024 * 1024)}MB.")
            
            # Reset pointer to the beginning of the file for further operations if needed
            image_file.seek(0)
            return img_format
    
    except IOError:
        raise ValueError("Unable to open the image. The file may not be a valid image.")

def upload_image_to_s3(base64_image: str, object_name:str) -> str:
    image = decode_base64_image(base64_image)
    try:
        s3_client.put_object(
            Bucket = BUCKET_NAME,
            Body = image,
            ContentType = 'image/jpeg',
            Key = object_name)
        logging.info(f"File uploaded to S3 bucket '{BUCKET_NAME}' as '{object_name}'.")
        return f"s3://{BUCKET_NAME}/{object_name}"
    except Exception as e:
        logging.error(f"Error uploading file as {object_name}: {e}")
        raise ValueError("Error uploading file to S3 bucket")

def decode_base64_image(base64_image: str):
    if base64_image.startswith('data:image'):
        base64_data = base64_image.split(",")[1]
    else:
        raise ValueError("Invalid base64 image format")
    try:
        image_data = base64.b64decode(base64_data)
    except Exception as e:
        raise ValueError(f"Error decoding base64 data: {str(e)}")

    return io.BytesIO(image_data)
    







