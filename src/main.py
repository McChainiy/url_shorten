from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.auth.dependencies import fastapi_users
from src.auth.backend import auth_backend
from src.auth.models import User
from src.auth.schemas import UserRead, UserCreate, UserUpdate

from src.routers.links import router as link_router
from src.routers.auth import router as auth_router
from src.redis import redis
from src.workers import stats_worker
from src.utils.expire_links import expire_service


import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    expire_task = asyncio.create_task(expire_service.run_periodic_cleanup(interval=10))
    asyncio.create_task(stats_worker())
    yield
    expire_service.stop()
    expire_task.cancel()
    await redis.close()

app = FastAPI(lifespan=lifespan)


#auth
app.include_router(auth_router)
#links
app.include_router(link_router)


@app.get("/")
def root():
    return {"message": "Welcome to URL Shortener Service"}
