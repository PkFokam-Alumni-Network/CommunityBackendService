import uvicorn
from fastapi import FastAPI
from typing import AsyncGenerator
from utils.init_db import create_tables
from routers import user_router, announcement_router
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    create_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(user_router.router)
app.include_router(announcement_router.router)


@app.get("/")
def read_root():
    return {"message": "Hello, PaaSCommunity!"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
