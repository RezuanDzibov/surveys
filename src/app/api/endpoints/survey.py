from typing import List

from fastapi import APIRouter, Depends
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.base import get_session
from app.models import User
from app.schemas.survey import SurveyCreate, SurveyOut, SurveyRetrieve
from app.services import survey as survey_services

router = APIRouter()


@router.post("", response_model=SurveyOut, status_code=201)
async def add_survey(
        survey_create: SurveyCreate,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    survey = await survey_services.create_survey(survey=survey_create, user_id=current_user.id, session=session)
    return survey


@router.get("/{id_}", response_model=SurveyRetrieve, status_code=200)
async def get_survey(
        id_: UUID4,
        session: AsyncSession = Depends(get_session),
):
    survey = await survey_services.get_survey(session=session, id_=id_)
    return survey


@router.get("", response_model=List[SurveyOut])
async def get_surveys(session: AsyncSession = Depends(get_session)):
    surveys = await survey_services.get_surveys(session=session)
    return surveys
