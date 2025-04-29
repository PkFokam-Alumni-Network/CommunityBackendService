from fastapi import APIRouter, Query, status, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database import get_db
from schemas import user_schema
from services.user_service import UserService
from logging_config import LOGGER

router = APIRouter()

@router.post("/login/", status_code=status.HTTP_200_OK, response_model=user_schema.UserLoginResponse)
def login(user: user_schema.UserLogin, session: Session = Depends(get_db)) -> user_schema.UserLoginResponse:
    service = UserService(session=session)
    try:
        user.email = user.email.lower()
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

@router.get("/users/", status_code=status.HTTP_200_OK)
def get_all_users(session: Session = Depends(get_db), counts: bool = Query(False, alias="counts"), active: bool = Query(False, alias="active")):
    service = UserService(session=session)
    users = service.get_users(active=active)
    if counts:
        return {"count": len(users)}
    return users

@router.get("/users/{user_id}", status_code=status.HTTP_200_OK, response_model=user_schema.UserGetResponseWithId)
def get_user_by_id(user_id: int, session: Session = Depends(get_db)) -> user_schema.UserGetResponseWithId:
    service = UserService(session=session)
    user = service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/users/{user_id}/mentees", status_code=status.HTTP_200_OK, response_model= list[user_schema.UserCreatedResponse])
def get_mentees(user_id: int, session: Session = Depends(get_db)) -> user_schema.UserCreatedResponse:
    service = UserService(session=session)
    mentees = service.get_mentees(user_id)
    return mentees

@router.put("/users/{user_id}", status_code=status.HTTP_200_OK, response_model=user_schema.UserGetResponse)
def update_user(user_id: int, user_data: user_schema.UserUpdate,
                session: Session = Depends(get_db)) -> user_schema.UserUpdate:
    user_service = UserService(session=session)
    try:
        updated_user = user_service.update_user(user_id=user_id, updated_data=user_data.model_dump(exclude_unset=True))
        return updated_user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put("/users/{user_id}/update-email", status_code=status.HTTP_200_OK, response_model=user_schema.UserGetResponse)
def update_user_email(user_id: int, body: user_schema.EmailUpdate, session: Session = Depends(get_db)) -> user_schema.UserGetResponse:
    service = UserService(session=session)
    try:
        updated_user = service.update_user_email(user_id=user_id, new_email=body.new_email)
        return updated_user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.put("/users/{user_id}/update-password", status_code=status.HTTP_200_OK, response_model=user_schema.UserGetResponse)
def update_user_password(user_id: int, body: user_schema.PasswordUpdate, session: Session = Depends(get_db)) -> user_schema.UserGetResponse:
    service = UserService(session=session)
    try:
        updated_user = service.update_password(old_password=body.old_password, new_password=body.new_password, user_id=user_id)
        return updated_user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.put("/users/{user_id}/profile-picture", status_code=200,response_model=user_schema.UserUpdate)  
def update_profile_picture(user_id: int, body: user_schema.ProfilePictureUpdate, session: Session = Depends(get_db)) -> str:
    service = UserService(session=session)
    try:
        image_path = service.save_profile_picture(user_id, body.base64_image)
    except Exception as e:
        LOGGER.error("Internal error while updating image, ", e)
        raise HTTPException(status_code=500, detail=f"Error saving the file: {str(e)}")
    return JSONResponse({"image_path":image_path})

@router.delete("/users/{user_id}", status_code=status.HTTP_200_OK, response_model=user_schema.UserDeletedResponse)
def delete_user(user_id: int, session: Session = Depends(get_db)) -> user_schema.UserDeletedResponse:
    service = UserService(session=session)
    try:
        service.remove_user(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return user_schema.UserDeletedResponse(message=f"user with email {user_id} was successfully deleted")

@router.get("/internal/users/", status_code=status.HTTP_200_OK, response_model= list[user_schema.UserGetResponseInternal])
def get_all_users_internal( session: Session = Depends(get_db)):
    service = UserService(session=session)
    users = service.get_users()
    return users

@router.post("/password-reset", status_code=status.HTTP_200_OK, response_model=user_schema.PasswordResetRequestResponse)
def request_password_reset(body:user_schema.PasswordResetRequest
                           ,session: Session = Depends(get_db)) -> user_schema.PasswordResetRequestResponse:
    service = UserService(session=session)
    try:
        service.request_password_reset(body.email)
        masked = f"{body.email[:3]}****"
        return user_schema.PasswordResetRequestResponse(
            message = f"Your reset link has been sent to your email starting with {masked}"
        )
    except ValueError as e:
        LOGGER.error(f"Value error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        LOGGER.error(f"Unexpected error: {str(e), body.email}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
    
@router.put("/password-reset", status_code=status.HTTP_200_OK, response_model=user_schema.UserUpdate)
def reset_password(body: user_schema.PasswordReset,
                   session: Session = Depends(get_db)) -> user_schema.UserUpdate:
        service = UserService(session=session)
        try:
            updated_user = service.reset_password(body.new_password, body.token)
            return updated_user
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error ")