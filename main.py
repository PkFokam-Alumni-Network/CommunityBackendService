from fastapi.security import HTTPBasicCredentials
import uvicorn
from fastapi import Depends, FastAPI, Response
from typing import AsyncGenerator
from auth import set_session_cookie, verify_credentials
from utils.init_db import create_tables
from routers import user_router, announcement_router
from docs import router as docs_router
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    create_tables()
    yield

origins = [
    "https://pkfalumni.com",
    "http://localhost:3000",
    "https://backoffice.pkfalumni.com",
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
app.include_router(docs_router)

@app.get("/")
async def read_root(
    response: Response,
    credentials: HTTPBasicCredentials = Depends(verify_credentials)
):
    set_session_cookie(response)
    return {"message": "Logged in successfully"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000,proxy_headers=True, forwarded_allow_ips="*")
