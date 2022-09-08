from typing import List, Union, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import subqueryload

from app.models import Survey, SurveyAttribute
from app.schemas.survey import SurveyCreate
from app.services import base as base_services


async def create_survey(session: AsyncSession, user_id: UUID, survey: SurveyCreate):
    data = survey.dict()
    attrs = data.pop("attrs")
    data["user_id"] = str(user_id)
    survey = await base_services.insert_object(
        session=session,
        model=Survey,
        to_insert=data,
    )
    await create_survey_attrs(session=session, survey_id=str(survey.id), attrs=attrs)
    return survey


async def create_survey_attrs(session: AsyncSession, survey_id: str, attrs: List[dict]):
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


async def get_surveys(session: AsyncSession, available: Optional[bool] = None) -> Union[List, List[Survey]]:
    statement = select(Survey).order_by(Survey.name, Survey.created_at, Survey.id)
    if isinstance(available, bool):
        statement = statement.where(Survey.available == available)
    result = await session.execute(statement=statement)
    surveys = result.scalars().all()
    return surveys
