from fastapi import APIRouter

from api.api_v1.endpoints.auth import router as auth_router
from api.api_v1.endpoints.user import router as user_router

router = APIRouter(prefix="/api/api_v1")

router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(user_router, prefix="/users", tags=["user"])
