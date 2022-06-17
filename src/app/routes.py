from fastapi import APIRouter

from auth.endpoints import auth_router
from user.endpoints import user_router


routes = APIRouter()

routes.include_router(auth_router, prefix="/auth", tags=["auth"])
routes.include_router(user_router, prefix="/user", tags=["user"])
