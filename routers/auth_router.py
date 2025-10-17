from fastapi import APIRouter, status, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from core.database import get_db
from schemas import user_schema
from services.auth_service import AuthService
from services.user_service import UserService
from core.logging_config import LOGGER
from utils.func_utils import decode_jwt

router = APIRouter(tags=["Authentication"])
WEEK = 86400 * 7
@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=user_schema.UserLoginResponse,
)
def login(
    user: user_schema.UserLogin, response: Response, session: Session = Depends(get_db)
) -> user_schema.UserLoginResponse:
    service = AuthService()
    masked_email = user.email[:3] + "****"
    try:
        login_response = service.login(session, user.email.lower(), user.password)
        response.set_cookie(
            key="session_token",
            value=login_response.access_token,
            httponly=True,
            secure=True,
            samesite="none",
            max_age=WEEK
        )
        return login_response
    except ValueError as e:
        LOGGER.warning(f"Login failed for {masked_email}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        LOGGER.error(f"SERVER ERROR in login for {masked_email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )

@router.post("/logout")
def logout(response: Response, db: Session = Depends(get_db), session_token: str | None = None):
    service = AuthService()
    if not session_token:
        raise HTTPException(status_code=401, detail="No active session found")
    service.logout(db, session_token)
    LOGGER.info("User logged out successfully")
    response.delete_cookie("session_token")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.post(
    "/auth/password-reset",
    status_code=status.HTTP_200_OK,
    response_model=user_schema.UserUpdate,
)
def reset_password(
    body: user_schema.PasswordReset, session: Session = Depends(get_db)
) -> user_schema.UserUpdate:
    service = UserService()
    try:
        decoded:dict = decode_jwt(body.token)
        email = decoded.get("user_id")
        if not email:
            raise ValueError("Invalid token")
        user = service.get_user_by_email(session, email)
        if not user:
            raise ValueError("User not found")
        return service.reset_password(session, user.id, body.new_password)
    except ValueError as e:
        LOGGER.error(f"Password reset failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        LOGGER.error(f"SERVER ERROR in reset_password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
