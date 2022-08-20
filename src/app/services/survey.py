from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from models import Survey, SurveyAttribute
from schemas.survey import SurveyCreate
from services import base as base_services


async def create_survey(session: AsyncSession, user_id: UUID, survey: SurveyCreate):
    data = survey.dict()
    attrs = data.pop("attrs")
    data["user_id"] = str(user_id)
    survey = await base_services.insert_object(
        session=session,
        model=Survey,
        to_insert=data,
    )
    await _create_survey_attributes(session=session, attrs=attrs)
    return survey


async def _create_survey_attributes(session: AsyncSession, attrs: List[dict]):
    attrs = [SurveyAttribute(**attr) for attr in attrs]
    session.add_all(attrs)
    await session.commit()
