from fastapi import APIRouter, status, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session
from database import get_db
from schemas import user_schema
from services.user_service import UserService
from utils.func_utils import get_password_hash


router = APIRouter()

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
        )
        return new_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/users/{user_email}", status_code=status.HTTP_200_OK, response_model=user_schema.UserCreatedResponse)
def get_user(user_email: str, session: Session = Depends(get_db)):
    service = UserService(session=session)
    user = service.get_user_details(user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/users/{user_email}", status_code=status.HTTP_200_OK, response_model = user_schema.UserDeletedResponse)
def delete_user(user_email: str, session: Session = Depends(get_db)) -> user_schema.UserDeletedResponse:
    service = UserService(session=session)
    try:
        service.remove_user(user_email)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return user_schema.UserDeletedResponse(message=f"user with email{user_email}, was successfully deleted")
  
@router.post("/users/{user_email}/profile-picture", status_code=200,response_model=user_schema.UpdatedProfilePictureResponse)  
def Update_profile_picture(user_email: str, image: UploadFile, session: Session = Depends(get_db)) -> user_schema.UpdatedProfilePictureResponse:
    service = UserService(session=session)
    try:
        service.Update_profile_picture(user_email, image)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Error saving the file: {str(e)}")
    return user_schema.UpdatedProfilePictureResponse(message="Profile picture was successfully Updated")

@router.delete("/users/{user_email}/profile-picture", status_code=200, response_model=user_schema.DeletedProfilePictureResponse) 
def delete_profile_picture(user_email: str, session: Session = Depends(get_db)) -> user_schema.DeletedProfilePictureResponse:
    service = UserService(session=session)
    try:
        service.delete_profile_picture(user_email)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Error deleting the file: {str(e)}")
    return user_schema.DeletedProfilePictureResponse(message="Profile picture was successfully deleted")

        
            