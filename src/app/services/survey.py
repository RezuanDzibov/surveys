from typing import List, Union
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import subqueryload

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
    await _create_survey_attributes(session=session, survey_id=str(survey.id), attrs=attrs)
    return survey


async def _create_survey_attributes(session: AsyncSession, survey_id: str, attrs: List[dict]):
    for attr in attrs:
        attr["survey_id"] = survey_id
    attrs = [SurveyAttribute(**attr) for attr in attrs]
    session.add_all(attrs)
    await session.commit()


async def get_survey(session: AsyncSession, id_: str):
    statement = select(Survey) \
        .options(subqueryload(Survey.attrs) \
        .load_only(SurveyAttribute.id, SurveyAttribute.question, SurveyAttribute.required)) \
        .where(Survey.id == id_)
    survey = await base_services.get_object(session=session, statement=statement)
    return survey


async def get_surveys(session: AsyncSession) -> Union[List, List[Survey]]:
    surveys = await base_services.get_objects(session=session, model=Survey)
    return surveys
