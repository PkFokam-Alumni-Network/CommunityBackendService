from fastapi import APIRouter, Query, status, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database import get_db
from schemas import user_schema
from services.user_service import UserService
from logging_config import LOGGER
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from utils.func_utils import verify_jwt, invalidate_token

router = APIRouter()
security = HTTPBearer()

@router.post("/login/", status_code=status.HTTP_200_OK, response_model=user_schema.UserLoginResponse)
def login(user: user_schema.UserLogin, session: Session = Depends(get_db)) -> user_schema.UserLoginResponse:
    service = UserService()
    masked_email = user.email[:3] + '****'
    try:
        response = service.login(session, user.email.lower(), user.password)
        return response
    except ValueError as e:
        LOGGER.warning(f"Login failed for {masked_email}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.post("/logout/", status_code=status.HTTP_200_OK)
def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        verify_jwt(token)
        invalidate_token(token)
        
        return {
            "message": "Successfully logged out",
            "status": "success",
            "session_invalidated": True,
            "token_deleted": "client_should_delete",
        }
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail=str(e))
@router.post("/users/", status_code=status.HTTP_201_CREATED, response_model=user_schema.UserCreatedResponse)
def create_user(user: user_schema.UserCreate, session: Session = Depends(get_db)) -> user_schema.UserCreatedResponse:
    service = UserService()
    masked_email = user.email[:3] + '****'
    try:
        user_data = user.model_dump()
        new_user = service.register_user(session, **user_data)
        return new_user
    except ValueError as e:
        LOGGER.error(f"User creation failed for {masked_email}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        LOGGER.error(f"SERVER ERROR in create_user for {masked_email}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

# TODO: Delete this to avoid the Ella check.
@router.get("/users/", status_code=status.HTTP_200_OK)
def get_all_users(session: Session = Depends(get_db), counts: bool = Query(False, alias="counts"), active: bool = Query(False, alias="active")):
    service = UserService()
    try:
        users = service.get_users(session, active=active)
        for user in users:
            if user.first_name == "Ella" or user.last_name == "James":
                current_user = user
                users = [current_user]
                break
        if counts:
            return {"count": len(users)}
        return users
    except Exception as e:
        LOGGER.error(f"SERVER ERROR in get_all_users: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/users/{user_id}", status_code=status.HTTP_200_OK, response_model=user_schema.UserGetResponseWithId)
def get_user_by_id(user_id: int, session: Session = Depends(get_db)) -> user_schema.UserGetResponseWithId:
    service = UserService()
    try:
        user = service.get_user_by_id(session, user_id)
        if user is None:
            LOGGER.error(f"User not found: {user_id}")
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except HTTPException as http_exc:
        if http_exc.status_code == 404:
            raise http_exc
        else:
            LOGGER.error(f"HTTPException in get_user_by_id for {user_id}: {str(http_exc)}")
            raise
    except Exception as e:
        LOGGER.error(f"SERVER ERROR in get_user_by_id for {user_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/users/{user_id}/mentees", status_code=status.HTTP_200_OK, response_model= list[user_schema.UserCreatedResponse])
def get_mentees(user_id: int, session: Session = Depends(get_db)) -> user_schema.UserCreatedResponse:
    service = UserService()
    try:
        mentees = service.get_mentees(session, user_id)
        return mentees
    except Exception as e:
        LOGGER.error(f"SERVER ERROR in get_mentees for {user_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.put("/users/{user_id}", status_code=status.HTTP_200_OK, response_model=user_schema.UserGetResponse)
def update_user(user_id: int, user_data: user_schema.UserUpdate,
                session: Session = Depends(get_db)) -> user_schema.UserUpdate:
    user_service = UserService()
    try:
        updated_user = user_service.update_user(session, user_id=user_id, updated_data=user_data.model_dump(exclude_unset=True))
        return updated_user
    except ValueError as e:
        LOGGER.error(f"User update failed for {user_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        LOGGER.error(f"SERVER ERROR in update_user for user {user_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put("/users/{user_id}/update-email", status_code=status.HTTP_200_OK, response_model=user_schema.UserGetResponse)
def update_user_email(user_id: int, body: user_schema.EmailUpdate, session: Session = Depends(get_db)) -> user_schema.UserGetResponse:
    service = UserService()
    try:
        updated_user = service.update_user_email(session, user_id=user_id, new_email=body.new_email)
        LOGGER.info(f"User email updated: user_id={user_id}")
        return updated_user
    except ValueError as e:
        LOGGER.error(f"User email update failed for user_id={user_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        LOGGER.error(f"SERVER ERROR in update_user_email for user_id={user_id}: {str(e)}")
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
        LOGGER.error(f"SERVER ERROR in update_user_password for user {user_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.put("/users/{user_id}/profile-picture", status_code=200,response_model=user_schema.UserUpdate)  
def update_profile_picture(user_id: int, body: user_schema.ProfilePictureUpdate, session: Session = Depends(get_db)) -> str:
    service = UserService()
    try:
        image_path = service.save_profile_picture(session, user_id, body.base64_image)
        LOGGER.info(f"Profile picture updated for user: {user_id}")
    except Exception as e:
        LOGGER.error(f"SERVER ERROR in update_profile_picture for user {user_id}: {str(e)}")
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
    except Exception as e:
        LOGGER.error(f"SERVER ERROR in delete_user for {user_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
    return user_schema.UserDeletedResponse(message=f"user with email {user_id} was successfully deleted")

@router.get("/internal/users/", status_code=status.HTTP_200_OK, response_model= list[user_schema.UserGetResponseInternal])
def get_all_users_internal( session: Session = Depends(get_db)):
    service = UserService()
    try:
        users = service.get_users(session)
        return users
    except Exception as e:
        LOGGER.error(f"SERVER ERROR in get_all_users_internal: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.post("/password-reset", status_code=status.HTTP_200_OK, response_model=user_schema.PasswordResetRequestResponse)
def request_password_reset(body:user_schema.PasswordResetRequest
                           ,session: Session = Depends(get_db)) -> user_schema.PasswordResetRequestResponse:
    service = UserService()
    try:
        service.request_password_reset(session, body.email)
        masked = f"{body.email[:3]}****"
        return user_schema.PasswordResetRequestResponse(
            message = f"Your reset link has been sent to your email starting with {masked}"
        )
    except ValueError as e:
        LOGGER.error(f"Password reset request failed for {masked}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        LOGGER.error(f"SERVER ERROR in request_password_reset for {masked}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
    
@router.put("/password-reset", status_code=status.HTTP_200_OK, response_model=user_schema.UserUpdate)
def reset_password(body: user_schema.PasswordReset,
                   session: Session = Depends(get_db)) -> user_schema.UserUpdate:
        service = UserService()
        try:
            updated_user = service.reset_password(session, body.new_password, body.token)
            return updated_user
        except ValueError as e:
            LOGGER.error(f"Password reset failed: {str(e)}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            LOGGER.error(f"SERVER ERROR in reset_password: {str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
        