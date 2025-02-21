import os
import uvicorn
from fastapi import HTTPException, security, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi import Depends, FastAPI
from typing import AsyncGenerator
from utils.init_db import create_tables
from routers import user_router, announcement_router
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    create_tables()
    yield

origins = [
    "https://pkfalumni.com",
    "http://localhost:3000",
]

app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(user_router.router)
app.include_router(announcement_router.router)

security = HTTPBasic()
def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = os.getenv("DOCS_AUTH_USERNAME")
    correct_password = os.getenv("DOCS_AUTH_PASSWORD")
    if credentials.username != correct_username or credentials.password != correct_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

@app.get("/docs")
async def get_docs(credentials: HTTPBasicCredentials = Depends(verify_credentials)):
      return get_swagger_ui_html(openapi_url="/openapi.json", title="API Docs")

@app.get("/")
def read_root():
    return {"message": "Hello, PaaSCommunity!"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000,proxy_headers=True, forwarded_allow_ips="*")
