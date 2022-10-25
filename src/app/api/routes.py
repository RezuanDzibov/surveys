from fastapi import APIRouter

from app.api.endpoints.answer import router as answer_router
from app.api.endpoints.auth import router as auth_router
from app.api.endpoints.survey import router as survey_router
from app.api.endpoints.user import router as user_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(user_router, prefix="/user", tags=["user"])
router.include_router(survey_router, prefix="/survey", tags=["survey"])
router.include_router(answer_router, prefix="/answer", tags=["answer"])
