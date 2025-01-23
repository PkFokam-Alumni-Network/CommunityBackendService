import uvicorn
from fastapi import FastAPI
from typing import AsyncGenerator
from utils.init_db import create_tables
from routers import user_router, announcement_router
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    create_tables()
    yield

origins = [
    "https://pkfalumni.com",
    "http://localhost:3000",
]
app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["api.pfkalumni.com", "pkfalumni.com"]
)
app.include_router(user_router.router)
app.include_router(announcement_router.router)


@app.get("/")
def read_root():
    return {"message": "Hello, PaaSCommunity!"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9000)
