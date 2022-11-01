from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select, delete
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import subqueryload
from sqlalchemy.orm.collections import InstrumentedList

from app.core.exceptions import raise_404
from app.models import Answer, Survey, SurveyAttribute, User, AnswerAttribute
from app.schemas import survey as schemas
from app.services import base as base_services


async def create_answer_attrs(session: AsyncSession, attrs: List[schemas.AnswerAttribute], answer_id: UUID):
    to_insert = list()
    for attr in attrs:
        attr = attr.dict()
        attr["answer_id"] = answer_id
        to_insert.append(AnswerAttribute(**attr))
    session.add_all(to_insert)
    await session.commit()
    return to_insert


class CreateAnswer:
    def __init__(self, session: AsyncSession, answer: schemas.BaseAnswer, user_id: UUID, survey_id: UUID):
        self._session = session
        self._answer = answer
        self._user_id = user_id
        self._survey_id = survey_id

    async def execute(self) -> Answer:
        await self._validate_answer()
        attrs = self._answer.attrs
        data = await self._prepare_data()
        inserted_answer = await self._insert_answer(data=data, attrs=attrs)
        return inserted_answer

    async def _validate_answer(self):
        statement = select(Survey).where(Survey.id == self._survey_id)
        if not await base_services.is_object_exists(session=self._session, where_statement=statement):
            await raise_404()
        statement = select(Answer).where(Answer.user_id == self._user_id, Answer.survey_id == self._survey_id)
        if await base_services.is_object_exists(session=self._session, where_statement=statement):
            raise HTTPException(status_code=409, detail="Answer is already exists")
        survey_attr_ids = [answer_attr.survey_attr_id for answer_attr in self._answer.attrs]
        statement = select(SurveyAttribute).where(
            SurveyAttribute.id.in_(
                survey_attr_ids
            )
        )
        result = await self._session.execute(statement)
        attrs = result.scalars().all()
        if len(self._answer.attrs) != len(attrs):
            not_exist_survey_attrs = ", ".join(
                [str(id_) for id_ in (set(survey_attr_ids).difference([attr.id for attr in attrs]))]
            )
            raise HTTPException(
                status_code=404,
                detail=f"Got not exist survey attributes with ids: [{not_exist_survey_attrs}]"
            )

    async def _prepare_data(self) -> dict:
        data = self._answer.dict(exclude={"attrs"})
        data["user_id"] = self._user_id
        data["survey_id"] = self._survey_id
        return data

    async def _insert_answer(self, data: dict, attrs: List[schemas.AnswerAttribute]) -> Answer:
        answer = await base_services.insert_object(
            session=self._session,
            model=Answer,
            to_insert=data,
        )
        attrs = await create_answer_attrs(session=self._session, attrs=attrs, answer_id=answer.id)
        answer.__dict__["attrs"] = InstrumentedList(attrs)
        return answer


async def delete_answer(session: AsyncSession, user: User, answer_id: UUID) -> None:
    try:
        statement = select(Answer.user_id).where(Answer.id == answer_id)
        result = await session.execute(statement)
        answer_user_id = result.one()[0]
        if answer_user_id != user.id:
            raise HTTPException(status_code=403, detail="You aren't author of this answer")
        statement = delete(Answer).where(Answer.id == answer_id)
        await session.execute(statement)
        await session.commit()
    except NoResultFound:
        await raise_404()


async def get_answer(session: AsyncSession, answer_id: UUID, user: Optional[User] = None) -> Answer:
    try:
        statement = select(Answer).options(subqueryload(Answer.attrs)).where(Answer.id == answer_id)
        result = await session.execute(statement)
        answer = result.one()[0]
        if not answer.available:
            if not user or answer.user_id != user.id:
                raise HTTPException(status_code=403, detail="You aren't author of this answer")
        return answer
    except NoResultFound:
        await raise_404()
