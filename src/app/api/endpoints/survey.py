from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_user
from db.base import get_session
from models import User
from schemas.survey import SurveyCreate, SurveyOut
from services.survey import create_survey

router = APIRouter()


@router.post("", response_model=SurveyOut, status_code=201)
async def add_survey(
        survey_create: SurveyCreate,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    survey = await create_survey(survey=survey_create, user_id=current_user.id, session=session)
    return survey
