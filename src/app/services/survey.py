from typing import List, Union, Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select, delete
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import subqueryload
from sqlalchemy.orm.collections import InstrumentedList

from app.core.exceptions import raise_404
from app.models import Survey, SurveyAttribute, User, Answer, AnswerAttribute
from app.schemas import survey as schemas
from app.services import base as base_services
from app.services.base import update_object


async def create_survey(session: AsyncSession, user_id: UUID, survey: schemas.SurveyCreate):
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


async def get_survey(session: AsyncSession, id_: UUID, user: Optional[User] = None):
    statement = select(Survey) \
        .options(subqueryload(Survey.attrs) \
        .load_only(SurveyAttribute.id, SurveyAttribute.question, SurveyAttribute.required, SurveyAttribute.available)) \
        .where(Survey.id == id_)
    survey = await base_services.get_object(session=session, statement=statement)
    if not user or user.id != survey.user_id:
        survey.__dict__["attrs"] = InstrumentedList(list(filter(lambda obj: obj.available is True, survey.attrs)))
    return survey


async def get_surveys(session: AsyncSession) -> Union[List, List[Survey]]:
    statement = select(Survey).order_by(Survey.name, Survey.created_at, Survey.id).where(Survey.available == True)
    result = await session.execute(statement=statement)
    surveys = result.scalars().all()
    return surveys


async def update_survey(session: AsyncSession, user: User, id_: UUID, to_update: schemas.SurveyUpdate) -> Survey:
    survey = await get_survey(session=session, user=user, id_=id_)
    if user.id != survey.user_id:
        raise HTTPException(status_code=403, detail="You can't edit this survey.")
    survey = await update_object(
        session=session,
        model=Survey,
        where_statements=[Survey.id == id_],
        to_update=to_update.dict(exclude_unset=True)
    )
    return survey


async def update_survey_attribute(
        session: AsyncSession,
        user: User,
        id_: UUID,
        to_update: schemas.SurveyAttributeUpdate
) -> SurveyAttribute:
    statement = select(SurveyAttribute.survey_id).where(SurveyAttribute.id == id_)
    result = await session.execute(statement=statement)
    try:
        survey_id = result.scalars().one()
    except NoResultFound:
        await raise_404()
    statement = select(Survey.user_id).where(Survey.id == survey_id)
    result = await session.execute(statement=statement)
    try:
        user_id = result.scalars().one()
    except NoResultFound:
        await raise_404()
    if user.id != user_id:
        raise HTTPException(status_code=403, detail="You can't edit this survey attr.")
    survey_attr = await base_services.update_object(
        session=session,
        model=SurveyAttribute,
        where_statements=[SurveyAttribute.id == id_],
        to_update=to_update.dict(exclude_unset=True)
    )
    return survey_attr


async def get_current_user_surveys(
        session: AsyncSession,
        user: User,
        available: Optional[bool] = None
) -> Union[list, List[Survey]]:
    statement = select(Survey).order_by(Survey.name, Survey.created_at, Survey.id).where(Survey.user_id == user.id)
    if isinstance(available, bool):
        statement = statement.where(Survey.available == available)
    result = await session.execute(statement=statement)
    surveys = result.scalars().all()
    return surveys


async def get_user_surveys(
        session: AsyncSession,
        user_id: UUID,
) -> Union[list, List[Survey]]:
    if not await base_services.is_object_exists(session=session, where_statement=select(User).where(User.id == user_id)):
        await raise_404()
    statement = select(Survey).order_by(Survey.name, Survey.created_at, Survey.id).where(
        Survey.user_id == user_id,
        Survey.available is True
    )
    result = await session.execute(statement=statement)
    surveys = result.scalars().all()
    return surveys


async def delete_survey(session: AsyncSession, user: User, id_: UUID) -> Survey:
    statement = delete(Survey).where(Survey.id == id_, Survey.user_id == user.id).returning(Survey)
    result = await session.execute(statement)
    await session.commit()
    try:
        survey = Survey(**dict(result.one()))
        return survey
    except NoResultFound:
        await raise_404()


async def delete_survey_attribute(session: AsyncSession, user: User, id_: UUID) -> SurveyAttribute:
    statement = select(SurveyAttribute).join(
        SurveyAttribute.survey.and_(Survey.user_id == user.id)
    ).where(SurveyAttribute.id == id_)
    if not await base_services.is_object_exists(
            session=session,
            where_statement=statement
    ):
        await raise_404()
    statement = delete(SurveyAttribute).where(SurveyAttribute.id == id_).returning(SurveyAttribute)
    result = await session.execute(statement)
    await session.commit()
    try:
        survey_attr = SurveyAttribute(**dict(result.one()))
        return survey_attr
    except NoResultFound:
        await raise_404()


async def get_survey_attribute(session: AsyncSession, id_: UUID, user: User = None) -> SurveyAttribute:
    statement = select(SurveyAttribute, Survey.user_id).join(SurveyAttribute.survey).where(SurveyAttribute.id == id_)
    result = await session.execute(statement)
    try:
        attr, user_id = result.one()
        if attr.available is False:
            if not user or user.id != user_id:
                await raise_404()
        return attr
    except NoResultFound:
        await raise_404()


async def create_answer_attrs(session: AsyncSession, attrs: List[schemas.AnswerAttribute], answer_id: UUID):
    to_insert = list()
    for attr in attrs:
        attr = attr.dict()
        attr["answer_id"] = answer_id
        to_insert.append(AnswerAttribute(**attr))
    session.add_all(to_insert)
    await session.commit()
    return attrs


async def create_answer(session: AsyncSession, answer: schemas.BaseAnswer, user_id: UUID, survey_id: UUID) -> Answer:
    statement = select(Survey).where(Survey.id == survey_id)
    if not await base_services.is_object_exists(session=session, where_statement=statement):
        await raise_404()
    statement = select(Answer).where(Answer.user_id == user_id, Answer.survey_id == survey_id)
    if await base_services.is_object_exists(session=session, where_statement=statement):
        raise HTTPException(status_code=409, detail="Answer is already exists")
    data = answer.dict(exclude={"attrs"})
    attrs = answer.attrs
    data["user_id"] = user_id
    data["survey_id"] = survey_id
    answer = await base_services.insert_object(
        session=session,
        model=Answer,
        to_insert=data,
    )
    attrs = await create_answer_attrs(session=session, attrs=attrs, answer_id=answer.id)
    answer.__dict__["attrs"] = InstrumentedList(attrs)
    return answer
