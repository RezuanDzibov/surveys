from fastapi import APIRouter

from api.endpoints.auth import router as auth_router
from api.endpoints.survey import router as survey_router
from api.endpoints.user import router as user_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(user_router, prefix="/user", tags=["user"])
router.include_router(survey_router, prefix="/survey", tags=["survey"])
