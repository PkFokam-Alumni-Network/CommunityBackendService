import os
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import Response
from fastapi import Cookie

security = HTTPBasic()

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = os.getenv("DOCS_AUTH_USERNAME")
    correct_password = os.getenv("DOCS_AUTH_PASSWORD")
    
    if credentials.username != correct_username or credentials.password != correct_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": 'Basic realm="Please log in to view the docs"'},
        )

def set_session_cookie(response: Response):
    response.set_cookie(
        key="session_id",
        value="authenticated",
        max_age=30,  # Expires in 10 minutes
        httponly=True,  
        samesite="Strict"  
    )

def get_session_cookie(session_id: str = Cookie(None)) -> str:
    if session_id != "authenticated":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You need to log in to access the docs.",
            headers={"WWW-Authenticate": 'Basic realm="Please log in to view the docs"'}
        )
    return session_id
