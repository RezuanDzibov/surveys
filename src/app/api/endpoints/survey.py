from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_current_active_user, get_current_active_user_or_none
from app.db.base import get_session
from app.models import User
from app.schemas.survey import SurveyCreate, SurveyOut, SurveyUpdate, SurveyAttributeUpdate, \
    SurveyOwnerOut
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


@router.get("/user/me", response_model=List[SurveyOut])
async def get_current_user_surveys(
        available: Optional[bool] = None,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user),
):
    surveys = await survey_services.get_current_user_surveys(session=session, user=current_user, available=available)
    return surveys


@router.get("/user/{id_}", response_model=List[SurveyOut])
async def get_user_surveys(id_: UUID4, session: AsyncSession = Depends(get_session)):
    surveys = await survey_services.get_user_surveys(session=session, user_id=id_)
    return surveys


@router.get("/{id_}", response_model=SurveyOut | SurveyOwnerOut, status_code=200)
async def get_survey(
        id_: UUID4,
        session: AsyncSession = Depends(get_session),
        current_user: Optional[User] = Depends(get_current_active_user_or_none),
):
    survey = await survey_services.get_survey(session=session, user=current_user, id_=id_)
    if current_user and current_user.id == survey.user_id:
        return SurveyOwnerOut.from_orm(survey)
    return SurveyOut.from_orm(survey)


@router.get("", response_model=List[SurveyOut])
async def get_surveys(session: AsyncSession = Depends(get_session)):
    surveys = await survey_services.get_surveys(session=session)
    return surveys


@router.patch("/{id_}")
async def update_survey(
        id_: UUID4,
        to_update: SurveyUpdate,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_active_user)
):
    survey = await survey_services.update_survey(session=session, user=current_user, id_=id_, to_update=to_update)
    return survey


@router.patch("/attr/{id_}")
async def update_survey_attr(
        id_: UUID4,
        to_update: SurveyAttributeUpdate,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_active_user),
):
    survey_attr = await survey_services.update_survey_attribute(
        session=session,
        user=current_user,
        id_=id_,
        to_update=to_update
    )
    return survey_attr
