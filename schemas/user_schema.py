from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr

from models.user import User, UserRole

class UserCreate(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    password: str
    
    address: Optional[str] = None
    phone: Optional[str] = None
    image: Optional[str] = "https://www.w3schools.com/howto/img_avatar.png"
    bio: Optional[str] = None

    graduation_year: Optional[int] = None
    degree: Optional[str] = None
    major: Optional[str] = None

    current_occupation: Optional[str] = None


    linkedin_profile: Optional[str] = None
    instagram_profile: Optional[str] = None

    role: Optional[str] = "user"
    is_active: Optional[bool] = True
    
class UserCreatedResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    
    model_config = ConfigDict(from_attributes=True)

class UserGetResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    address: Optional[str]
    phone: Optional[str]
    image: Optional[str]
    bio: Optional[str]
    graduation_year: Optional[int]
    degree: Optional[str]
    major: Optional[str]
    current_occupation: Optional[str]
    linkedin_profile: Optional[str]
    instagram_profile: Optional[str]

class Attendee(BaseModel):
    image: Optional[str]
    first_name: str
    last_name: str
    
    model_config = ConfigDict(from_attributes=True)

class UserGetResponseWithId(UserGetResponse):
    id: int

class UserGetResponseInternal(UserGetResponse):
    role: UserRole = UserRole.user
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

    model_config = ConfigDict(from_attributes=True)

class UserDeletedResponse(BaseModel):
    message: str

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    image: Optional[str] = None
    bio: Optional[str] = None
    graduation_year: Optional[int] = None
    degree: Optional[str] = None
    major: Optional[str] = None
    current_occupation: Optional[str] = None
    linkedin_profile: Optional[str] = None
    instagram_profile: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None

class ProfilePictureUpdate(BaseModel):
    base64_image: str

class EmailUpdate(BaseModel):
    new_email: EmailStr

class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str

class PasswordReset(BaseModel):
    new_password: str
    token: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetRequestResponse(BaseModel):
    message: str

class UserLoginResponse(UserCreate):
    id: int
    access_token: str
    token_type: str = "bearer"

    @staticmethod
    def create_user_login_response(user:User, access_token:str):
        return UserLoginResponse(
            id = user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            password="Fake password",
            address=user.address,
            phone=user.phone,
            image=user.image,
            bio=user.bio,
            graduation_year=user.graduation_year,
            degree=user.degree,
            major=user.major,
            current_occupation=user.current_occupation,
            linkedin_profile=user.linkedin_profile,
            instagram_profile=user.instagram_profile,
            role=user.role,
            is_active=user.is_active,
            access_token=access_token
        )
        

