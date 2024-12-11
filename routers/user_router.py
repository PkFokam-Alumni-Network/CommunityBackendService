from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from models.user import User
from database import get_db
from schemas import user_schema
from utils.func_utils import get_password_hash


router = APIRouter()

@router.post("/users/", status_code=status.HTTP_201_CREATED, response_model=user_schema.UserOut)
def create_user(user: user_schema.UserCreate, db: Session = Depends(get_db)) -> user_schema.UserOut:
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if  existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create and add the new user
    hashed_password = get_password_hash(user.password)
    new_user = User(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        graduation_year=user.graduation_year,
        degree=user.degree,
        major=user.major,
        phone=user.phone,
        password=hashed_password,
        current_occupation=user.current_occupation,
        image=user.image,
        linkedin_profile=user.linkedin_profile,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.delete("/users/{user_email}", status_code=status.HTTP_200_OK, response_model=Deletion_response)
def delete_user(user_email: str, db: Session = Depends(get_db)) -> Deletion_response: 
    #Check if the user exists
    user = db.query(User).filter(User.email == user_email).first()
    
    if user is None:
        # if User does not exist, raise a 404 error
        raise HTTPException(status_code=404, detail = "User does not exist")
    #Delete existing user from db
    db.delete(user)
    db.commit()
    return {f"user with email{user_email}, was successfully deleted"}
    
