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
    service = UserService()
    try:
        response = service.login(session, user.email.lower(), user.password)
        LOGGER.info(f"User login successful: {user.email.lower()}")
        return response
    except ValueError as e:
        LOGGER.error(f"Login failed for {user.email.lower()}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.post("/users/", status_code=status.HTTP_201_CREATED, response_model=user_schema.UserCreatedResponse)
def create_user(user: user_schema.UserCreate, session: Session = Depends(get_db)) -> user_schema.UserCreatedResponse:
    service = UserService()
    try:
        user_data = user.model_dump()
        new_user = service.register_user(session, **user_data)
        LOGGER.info(f"User created: {user_data.get('email')}")
        return new_user
    except ValueError as e:
        LOGGER.error(f"User creation failed for {user.email}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# TODO: Delete this to avoid the Ella check.
@router.get("/users/", status_code=status.HTTP_200_OK)
def get_all_users(session: Session = Depends(get_db), counts: bool = Query(False, alias="counts"), active: bool = Query(False, alias="active")):
    service = UserService()
    users = service.get_users(session, active=active)

    for user in users:
        if user.first_name == "Ella" or user.last_name == "James":
            current_user = user
            users = [current_user]
            break
    if counts:
        LOGGER.info(f"Returning user count: {len(users)}")
        return {"count": len(users)}
    LOGGER.info(f"Returning users list, count: {len(users)}")
    return users

@router.get("/users/{user_id}", status_code=status.HTTP_200_OK, response_model=user_schema.UserGetResponseWithId)
def get_user_by_id(user_id: int, session: Session = Depends(get_db)) -> user_schema.UserGetResponseWithId:
    service = UserService()
    user = service.get_user_by_id(session, user_id)
    if user is None:
        LOGGER.error(f"User not found: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    LOGGER.info(f"User retrieved: {user_id}")
    return user

@router.get("/users/{user_id}/mentees", status_code=status.HTTP_200_OK, response_model= list[user_schema.UserCreatedResponse])
def get_mentees(user_id: int, session: Session = Depends(get_db)) -> user_schema.UserCreatedResponse:
    service = UserService()
    mentees = service.get_mentees(session, user_id)
    LOGGER.info(f"Mentees retrieved for user: {user_id}, count: {len(mentees)}")
    return mentees

@router.put("/users/{user_id}", status_code=status.HTTP_200_OK, response_model=user_schema.UserGetResponse)
def update_user(user_id: int, user_data: user_schema.UserUpdate,
                session: Session = Depends(get_db)) -> user_schema.UserUpdate:
    user_service = UserService()
    try:
        updated_user = user_service.update_user(session, user_id=user_id, updated_data=user_data.model_dump(exclude_unset=True))
        LOGGER.info(f"User updated: {user_id}")
        return updated_user
    except ValueError as e:
        LOGGER.error(f"User update failed for {user_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        LOGGER.error(f"Unexpected error updating user {user_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put("/users/{user_id}/update-email", status_code=status.HTTP_200_OK, response_model=user_schema.UserGetResponse)
def update_user_email(user_id: int, body: user_schema.EmailUpdate, session: Session = Depends(get_db)) -> user_schema.UserGetResponse:
    service = UserService()
    try:
        updated_user = service.update_user_email(session, user_id=user_id, new_email=body.new_email)
        LOGGER.info(f"User email updated: {user_id} to {body.new_email}")
        return updated_user
    except ValueError as e:
        LOGGER.error(f"User email update failed for {user_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        LOGGER.error(f"Unexpected error updating email for user {user_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.put("/users/{user_id}/update-password", status_code=status.HTTP_200_OK, response_model=user_schema.UserGetResponse)
def update_user_password(user_id: int, body: user_schema.PasswordUpdate, session: Session = Depends(get_db)) -> user_schema.UserGetResponse:
    service = UserService()
    try:
        updated_user = service.update_password(session, old_password=body.old_password, new_password=body.new_password, user_id=user_id)
        LOGGER.info(f"User password updated: {user_id}")
        return updated_user
    except ValueError as e:
        LOGGER.error(f"User password update failed for {user_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        LOGGER.error(f"Unexpected error updating password for user {user_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.put("/users/{user_id}/profile-picture", status_code=200,response_model=user_schema.UserUpdate)  
def update_profile_picture(user_id: int, body: user_schema.ProfilePictureUpdate, session: Session = Depends(get_db)) -> str:
    service = UserService()
    try:
        image_path = service.save_profile_picture(session, user_id, body.base64_image)
        LOGGER.info(f"Profile picture updated for user: {user_id}")
    except Exception as e:
        LOGGER.error(f"Internal error while updating image for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saving the file: {str(e)}")
    return JSONResponse({"image_path":image_path})

@router.delete("/users/{user_id}", status_code=status.HTTP_200_OK, response_model=user_schema.UserDeletedResponse)
def delete_user(user_id: int, session: Session = Depends(get_db)) -> user_schema.UserDeletedResponse:
    service = UserService()
    try:
        service.remove_user(session, user_id)
        LOGGER.info(f"User deleted: {user_id}")
    except ValueError as e:
        LOGGER.error(f"User deletion failed for {user_id}: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    return user_schema.UserDeletedResponse(message=f"user with email {user_id} was successfully deleted")

@router.get("/internal/users/", status_code=status.HTTP_200_OK, response_model= list[user_schema.UserGetResponseInternal])
def get_all_users_internal( session: Session = Depends(get_db)):
    service = UserService()
    users = service.get_users(session)
    LOGGER.info(f"Internal users list retrieved, count: {len(users)}")
    return users

@router.post("/password-reset", status_code=status.HTTP_200_OK, response_model=user_schema.PasswordResetRequestResponse)
def request_password_reset(body:user_schema.PasswordResetRequest
                           ,session: Session = Depends(get_db)) -> user_schema.PasswordResetRequestResponse:
    service = UserService()
    try:
        service.request_password_reset(session, body.email)
        masked = f"{body.email[:3]}****"
        LOGGER.info(f"Password reset requested for: {body.email}")
        return user_schema.PasswordResetRequestResponse(
            message = f"Your reset link has been sent to your email starting with {masked}"
        )
    except ValueError as e:
        LOGGER.error(f"Password reset request failed for {body.email}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        LOGGER.error(f"Unexpected error during password reset request for {body.email}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
    
@router.put("/password-reset", status_code=status.HTTP_200_OK, response_model=user_schema.UserUpdate)
def reset_password(body: user_schema.PasswordReset,
                   session: Session = Depends(get_db)) -> user_schema.UserUpdate:
        service = UserService()
        try:
            updated_user = service.reset_password(session, body.new_password, body.token)
            LOGGER.info(f"Password reset successful for token: {body.token}")
            return updated_user
        except ValueError as e:
            LOGGER.error(f"Password reset failed for token {body.token}: {str(e)}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            LOGGER.error(f"Unexpected error during password reset for token {body.token}: {str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error ")