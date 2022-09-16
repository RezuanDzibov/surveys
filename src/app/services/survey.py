from typing import List, Union, Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import subqueryload

from app.models import Survey, SurveyAttribute, User
from app.schemas.survey import SurveyCreate, SurveyUpdate, SurveyAttributeUpdate
from app.services import base as base_services
from app.services.base import update_object


async def create_survey(session: AsyncSession, user_id: UUID, survey: SurveyCreate):
    data = survey.dict()
    attrs = data.pop("attrs")
    data["user_id"] = user_id
    survey = await base_services.insert_object(
        session=session,
        model=Survey,
        to_insert=data,
    )
    await create_survey_attrs(session=session, survey_id=survey.id, attrs=attrs)
    return survey


async def create_survey_attrs(session: AsyncSession, survey_id: UUID, attrs: List[dict]) -> List[SurveyAttribute]:
    for attr in attrs:
        attr["survey_id"] = survey_id
    attrs = [SurveyAttribute(**attr) for attr in attrs]
    session.add_all(attrs)
    await session.commit()
    return attrs


async def get_survey(session: AsyncSession, id_: UUID):
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


async def update_survey(session: AsyncSession, user: User, id_: UUID, to_update: SurveyUpdate) -> Survey:
    survey = await get_survey(session=session, id_=id_)
    if user.id != survey.user_id:
        raise HTTPException(status_code=403, detail="You can't edit this survey.")
    survey = await update_object(session=session, model=Survey, where_statements=[Survey.id == id_], to_update=to_update.dict(exclude_unset=True))
    return survey


async def update_survey_attribute(
        session: AsyncSession,
        user: User,
        id_: UUID,
        to_update: SurveyAttributeUpdate
) -> SurveyAttribute:
    statement = select(SurveyAttribute.survey_id).where(SurveyAttribute.id == id_)
    result = await session.execute(statement=statement)
    try:
        survey_id = result.scalars().one()
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Not found")
    statement = select(Survey.user_id).where(Survey.id == survey_id)
    result = await session.execute(statement=statement)
    try:
        user_id = result.scalars().one()
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Not found")
    if user.id != user_id:
        raise HTTPException(status_code=403, detail="You can't edit this survey attr.")
    survey_attr = await base_services.update_object(
        session=session,
        model=SurveyAttribute,
        where_statements=[SurveyAttribute.id == id_],
        to_update=to_update.dict(exclude_unset=True)
    )
    return survey_attr
