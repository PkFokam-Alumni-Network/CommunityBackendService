import bcrypt

from services.user_service import UserService

def get_password_hash(password:str) -> str: 
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')