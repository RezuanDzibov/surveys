from fastapi import APIRouter

from app.auth.endpoints import router as auth_router
from app.user.endpoints import router as user_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(user_router, prefix="/users", tags=["user"])
