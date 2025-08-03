import uvicorn
from fastapi.responses import HTMLResponse
from fastapi import Depends, FastAPI, HTTPException
from typing import AsyncGenerator
from core.auth import get_current_username
import core.database as database
from sqlalchemy import text
from core.database import get_db
from routers import user_router, announcement_router, event_router
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from core.logging_config import LOGGER
from core.settings import settings
from datetime import datetime


# TODO: Init logging and use config/settings.py for env variables
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    database.init_db(settings.DATABASE_URL)
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
async def read_root():
    return {"message": "PACI API"}


@app.get("/docs", response_class=HTMLResponse)
async def get_docs(username: str = Depends(get_current_username)) -> HTMLResponse:
    return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")


@app.get("/redoc", response_class=HTMLResponse)
async def get_redoc(username: str = Depends(get_current_username)) -> HTMLResponse:
    return get_redoc_html(openapi_url="/openapi.json", title="redoc")


@app.get("/health")
async def health_check():
    try:
        db = next(get_db())
        try:
            result = db.execute(text("SELECT 1")).fetchone()
            if not result:
                raise HTTPException(status_code=503, detail="Database query failed")
        except Exception as db_error:
            LOGGER.error(f"Database health check failed: {str(db_error)}")
            raise HTTPException(status_code=503, detail="Database connection failed")
        finally:
            db.close()

        return {
            "status": "healthy",
            "service": "PACI Community Backend",
            "database": "connected",
            "timestamp": datetime.now().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        LOGGER.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unavailable")


if __name__ == "__main__":
    uvicorn.run(
        app, host="0.0.0.0", port=9000, proxy_headers=True, forwarded_allow_ips="*"
    )
