from fastapi import FastAPI
from src.auth.dependencies import fastapi_users
from src.auth.backend import auth_backend
from src.auth.models import User
from src.auth.schemas import UserRead, UserCreate, UserUpdate

from src.routers.links import router as link_router
from src.routers.auth import router as auth_router
app = FastAPI()


#auth
app.include_router(auth_router)
#links
app.include_router(link_router)


@app.get("/")
def root():
    return {"message": "Welcome to URL Shortener Service"}

