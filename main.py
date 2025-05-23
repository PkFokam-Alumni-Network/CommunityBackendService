import uvicorn
from fastapi.responses import HTMLResponse
from fastapi import Depends, FastAPI 
from typing import AsyncGenerator
from auth import get_current_username
import database
from routers import user_router, announcement_router, event_router
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from logging_config import LOGGER
from settings import settings

# TODO: Init logging and use config/settings.py for env variables
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    database.init_db(settings.database_url)
    database.Base.metadata.create_all(bind=database.engine)
    yield


app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(user_router.router)
app.include_router(announcement_router.router)
app.include_router(event_router.router)

@app.get("/")
async def read_root(
):
    return  {"message": "PACI API"}


@app.get("/docs", response_class=HTMLResponse)
async def get_docs(username: str = Depends(get_current_username)) -> HTMLResponse:
    return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")


@app.get("/redoc", response_class=HTMLResponse)
async def get_redoc(username: str = Depends(get_current_username)) -> HTMLResponse:
    return get_redoc_html(openapi_url="/openapi.json", title="redoc")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000,proxy_headers=True, forwarded_allow_ips="*")
