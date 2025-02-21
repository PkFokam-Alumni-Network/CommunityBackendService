from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database import get_db
from schemas import user_schema
from services.user_service import UserService
from utils.func_utils import get_password_hash

router = APIRouter()

@router.post("/login/", status_code=status.HTTP_200_OK, response_model=user_schema.UserLoginResponse)
def login(user: user_schema.UserLogin, session: Session = Depends(get_db)) -> user_schema.UserLoginResponse:
    service = UserService(session=session)
    try:
        response = service.login(user.email, user.password)
        return response
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.post("/users/", status_code=status.HTTP_201_CREATED, response_model=user_schema.UserCreatedResponse)
def create_user(user: user_schema.UserCreate, session: Session = Depends(get_db)) -> user_schema.UserCreatedResponse:
    service = UserService(session=session)
    try:
        new_user = service.register_user(
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            password=user.password,
            address=user.address,
            graduation_year=user.graduation_year,
            degree=user.degree,
            major=user.major,
            phone=user.phone,
            current_occupation=user.current_occupation,
            image=user.image,
            linkedin_profile=user.linkedin_profile,
            instagram_profile=user.instagram_profile,
            is_active=user.is_active,
            role=user.role,
            bio=user.bio,
            mentor_email=user.mentor_email,
        )
        return new_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/users/{user_email}", status_code=status.HTTP_200_OK, response_model=user_schema.UserGetResponse)
def get_user(user_email: str, session: Session = Depends(get_db)) -> user_schema.UserGetResponse:
    service = UserService(session=session)
    user = service.get_user_details(user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/users/", status_code=status.HTTP_200_OK, response_model= list[user_schema.UserGetResponse])
def get_all_users(session: Session = Depends(get_db)):
    service = UserService(session=session)
    users = service.get_users()
    return users

@router.get("/users/{user_email}/mentees", status_code=status.HTTP_200_OK, response_model= list[user_schema.UserCreatedResponse])
def get_mentees(mentor_email: str, session: Session = Depends(get_db)) -> user_schema.UserCreatedResponse:
    service = UserService(session=session)
    mentees = service.get_mentees(mentor_email)
    return mentees

@router.put("/users/{user_email}", status_code=status.HTTP_200_OK, response_model=user_schema.UserGetResponse)
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

@router.put("/users/{user_email}/update-email", status_code=status.HTTP_200_OK, response_model=user_schema.UserGetResponse)
def update_user_email(user_email: str, body: user_schema.EmailUpdate, session: Session = Depends(get_db)) -> user_schema.UserGetResponse:
    service = UserService(session=session)
    try:
        updated_user = service.update_user_email(current_email=user_email, new_email=body.email)
        return updated_user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.put("/users/{user_email}/update-password", status_code=status.HTTP_200_OK, response_model=user_schema.UserGetResponse)
def update_user_password(user_email: str, body: user_schema.PasswordUpdate, session: Session = Depends(get_db)) -> user_schema.UserGetResponse:
    service = UserService(session=session)
    try:
        updated_user = service.update_password(old_password=body.oldPassword, new_password=body.newPassword, email=user_email)
        return updated_user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.put("/users/{user_email}/profile-picture", status_code=200,response_model=user_schema.UserUpdate)  
def update_profile_picture(user_email: str, body: user_schema.ProfilePictureUpdate, session: Session = Depends(get_db)) -> str:
    service = UserService(session=session)
    try:
        image_path = service.save_profile_picture(user_email, body.base64_image)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Error saving the file: {str(e)}")
    return JSONResponse({"image_path":image_path})

@router.delete("/users/{user_email}", status_code=status.HTTP_200_OK, response_model=user_schema.UserDeletedResponse)
def delete_user(user_email: str, session: Session = Depends(get_db)) -> user_schema.UserDeletedResponse:
    service = UserService(session=session)
    try:
        service.remove_user(user_email)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return user_schema.UserDeletedResponse(message=f"user with email {user_email} was successfully deleted")


