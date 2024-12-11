from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    graduation_year: int
    degree: str
    major: str
    phone: str
    password: str
    current_occupation: str
    image: str
    linkedin_profile: str

class UserOut(BaseModel):
    email: str
    first_name: str
    last_name: str

class DeletionApproved(BaseModel):
    message: str
