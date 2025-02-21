from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasicCredentials
from auth import verify_credentials, get_session_cookie
from fastapi.openapi.docs import get_swagger_ui_html

router = APIRouter()

@router.get("/docs", response_class=HTMLResponse)
async def get_docs(
    credentials: HTTPBasicCredentials = Depends(verify_credentials),
    session_id: str = Depends(get_session_cookie)
):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="API Docs")
