from typing import List
from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AnswerAttribute, User, Survey, Answer
from app.schemas import survey as schemas
from app.services import answer as answer_services
from app.services import base as base_services
from tests.factories import AnswerAttributeFactory
from tests.utils import build_answer_attrs_with_survey_attrs


class TestCreateAnswer:
    async def test_success(
            self,
            admin_user: User,
            session: AsyncSession,
            factory_survey: Survey
    ):
        attrs = await build_answer_attrs_with_survey_attrs(survey=factory_survey)
        expected_answer = schemas.BaseAnswer(attrs=attrs)
        created_answer = await answer_services.CreateAnswer(
            session=session,
            answer=expected_answer,
            user_id=admin_user.id,
            survey_id=factory_survey.id
        ).execute()
        assert expected_answer == schemas.BaseAnswer.from_orm(created_answer)

    async def test_404_not_exist_survey_attr(
            self,
            admin_user: User,
            session: AsyncSession,
            factory_survey: Survey
    ):
        attrs = await build_answer_attrs_with_survey_attrs(survey=factory_survey)
        attr = AnswerAttributeFactory.build()
        attr.survey_attr_id = uuid4()
        attrs.append(attr.as_dict())
        expected_answer = schemas.BaseAnswer(attrs=attrs)
        with pytest.raises(HTTPException) as exception:
            await answer_services.CreateAnswer(
                session=session,
                answer=expected_answer,
                user_id=admin_user.id,
                survey_id=factory_survey.id
            ).execute()
            assert exception.value.status_code == 404

    async def test_409(
            self,
            admin_user: User,
            session: AsyncSession,
            build_answer_attrs: List[AnswerAttribute],
            factory_answer: Answer,
            factory_survey: Survey
    ):
        attrs = await build_answer_attrs_with_survey_attrs(survey=factory_survey)
        expected_answer = schemas.BaseAnswer(attrs=attrs)
        with pytest.raises(HTTPException) as exception:
            await answer_services.CreateAnswer(
                session=session,
                answer=expected_answer,
                user_id=admin_user.id,
                survey_id=factory_answer.survey_id
            ).execute()
            assert exception.value.status_code == 409

    async def test_not_exists_survey(
            self,
            admin_user: User,
            session: AsyncSession,
            build_answer_attrs: List[AnswerAttribute],
            factory_survey: Survey
    ):
        attrs = await build_answer_attrs_with_survey_attrs(survey=factory_survey)
        expected_answer = schemas.BaseAnswer(attrs=attrs)
        with pytest.raises(HTTPException) as exception:
            await answer_services.CreateAnswer(
                session=session,
                answer=expected_answer,
                user_id=admin_user.id,
                survey_id=uuid4()
            ).execute()
            assert exception.value.status_code == 404


class TestCreateAnswerAttributes:
    @pytest.mark.parametrize("factory_answer", [False], indirect=True)
    async def test_success(
            self,
            session: AsyncSession,
            factory_answer: Answer,
            build_answer_attrs: List[AnswerAttribute],
            factory_survey: Survey
    ):
        attrs = await build_answer_attrs_with_survey_attrs(survey=factory_survey)
        expected_attrs = [schemas.AnswerAttribute(**attr) for attr in attrs]
        created_attrs = await answer_services.create_answer_attrs(
            session=session,
            attrs=expected_attrs,
            answer_id=factory_answer.id
        )
        assert expected_attrs == [schemas.AnswerAttribute.from_orm(attr) for attr in created_attrs]


class TestDeleteAnswer:
    @pytest.mark.parametrize("factory_answer", [True], indirect=True)
    async def test_success(self, session: AsyncSession, admin_user: User, factory_answer: Answer):
        await answer_services.delete_answer(
            session=session,
            user=admin_user,
            answer_id=factory_answer.id

        )
        assert not await base_services.is_object_exists(
            session=session,
            where_statement=select(Answer).where(Answer.id == factory_answer.id)
        )
        survey_attr_ids = [answer_attr.id for answer_attr in factory_answer.attrs]
        statement = select(AnswerAttribute).where(
            AnswerAttribute.id.in_(
                survey_attr_ids
            )
        )
        result = await session.execute(statement)
        assert not result.scalars().all()

    async def test_404(self, session: AsyncSession, admin_user: User):
        with pytest.raises(HTTPException) as exception:
            await answer_services.delete_answer(
                session=session,
                user=admin_user,
                answer_id=uuid4()
            )
            assert exception.value.status_code == 404

    @pytest.mark.parametrize("factory_answer", [True], indirect=True)
    async def test_for_not_author(self, session: AsyncSession, factory_answer: Answer, user_and_its_pass: dict):
        with pytest.raises(HTTPException) as exception:
            await answer_services.delete_answer(
                session=session,
                user=user_and_its_pass["user"],
                answer_id=uuid4()
            )
            assert exception.value.status_code == 403
