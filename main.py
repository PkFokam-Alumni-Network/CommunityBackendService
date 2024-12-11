from fastapi import FastAPI
from models.user import Base
from database import engine
from routers import user_router
import uvicorn

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(user_router.router)

@app.get("/")
def read_root():
    return {"message": "Hello, PaaSCommunity!"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
