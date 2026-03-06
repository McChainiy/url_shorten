from fastapi import APIRouter
from src.auth.dependencies import fastapi_users, auth_backend
from src.auth.schemas import UserRead, UserCreate, UserUpdate

router = APIRouter()

router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)
# router.include_router(
#     fastapi_users.get_logout_router(auth_backend),
#     prefix="/auth",
#     tags=["auth"],
# )