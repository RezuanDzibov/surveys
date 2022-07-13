from fastapi import APIRouter

from app.auth.endpoints import router as auth_router
from app.user.endpoints import router as user_router


routes = APIRouter()

routes.include_router(auth_router, prefix="/auth", tags=["auth"])
routes.include_router(user_router, prefix="/user", tags=["user"])
