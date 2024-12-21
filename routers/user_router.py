from fastapi import APIRouter, status, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db
from schemas import user_schema
from services.user_service import UserService
from utils.func_utils import get_password_hash
from typing import List

router = APIRouter()

@router.post("/login/", status_code=status.HTTP_200_OK)
def login(user: user_schema.UserLogin, session: Session = Depends(get_db)):
    service = UserService(session=session)
    try:
        token = service.login(user.email, user.password)
        return {"access_token": token, "token_type": "bearer"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.post("/users/", status_code=status.HTTP_201_CREATED, response_model=user_schema.UserCreatedResponse)
def create_user(user: user_schema.UserCreate, session: Session = Depends(get_db)) -> user_schema.UserCreatedResponse:
    service = UserService(session=session)
    hashed_password = get_password_hash(user.password)
    try:
        new_user = service.register_user(
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            password=hashed_password,
            graduation_year=user.graduation_year,
            degree=user.degree,
            major=user.major,
            phone=user.phone,
            current_occupation=user.current_occupation,
            image=user.image,
            linkedin_profile=user.linkedin_profile,
            mentor_email=user.mentor_email,
        )
        return new_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/users/{user_email}", status_code=status.HTTP_200_OK, response_model=user_schema.UserCreatedResponse)
def get_user(user_email: str, session: Session = Depends(get_db)) -> user_schema.UserCreatedResponse:
    service = UserService(session=session)
    user = service.get_user_details(user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/users/", status_code=status.HTTP_200_OK, response_model= list[user_schema.UserCreatedResponse])
def get_user(session: Session = Depends(get_db)):
    service = UserService(session=session)
    users = service.get_users()
    return users

@router.put("/users/{user_email}", status_code=status.HTTP_200_OK, response_model=user_schema.UserUpdate)
def update_user(user_email: str, user_data: user_schema.UserUpdate,
                session: Session = Depends(get_db)) -> user_schema.UserUpdate:
    user_service = UserService(session=session)
    try:
        updated_user = user_service.update_user(email=user_email, updated_data=user_data.model_dump(exclude_unset=True))
        return updated_user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.delete("/users/{user_email}", status_code=status.HTTP_200_OK, response_model=user_schema.UserDeletedResponse)
def delete_user(user_email: str, session: Session = Depends(get_db)) -> user_schema.UserDeletedResponse:
    service = UserService(session=session)
    try:
        service.remove_user(user_email)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return user_schema.UserDeletedResponse(message=f"user with email{user_email}, was successfully deleted")
  
@router.put("/users/{user_email}/profile-picture", status_code=200,response_model=user_schema.UserUpdate)  
def update_picture(user_email: str, image: UploadFile, session: Session = Depends(get_db)) -> user_schema.UserUpdate:
    service = UserService(session=session)
    try:
        image_path = service.generate_profile_picture_path(user_email, image)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Error saving the file: {str(e)}")
    return service.update_user(user_email, {"image":image_path})

@router.delete("/users/{user_email}/profile-picture", status_code=200, response_model=user_schema.UserUpdate) 
def delete_profile_picture(user_email: str, session: Session = Depends(get_db)) -> user_schema.UserUpdate:
    service = UserService(session=session)
    try:
        service.delete_profile_picture(user_email)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Error deleting the file: {str(e)}")
    return service.update_user(user_email, {"image":None})

@router.get("/users/{user_email}/mentees", status_code=status.HTTP_200_OK, response_model= list[user_schema.UserCreatedResponse])
def get_mentees(mentor_email: str, session: Session = Depends(get_db)) -> user_schema.UserCreatedResponse:
    service = UserService(session=session)
    mentees = service.get_mentees(mentor_email)
    return mentees
