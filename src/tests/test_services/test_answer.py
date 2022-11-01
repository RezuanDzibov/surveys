import random
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
            factory_survey: Survey,
            build_answer: Answer
    ):
        expected_answer = schemas.BaseAnswer.from_orm(build_answer)
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
            factory_survey: Survey,
            build_answer: Answer
    ):
        attr = AnswerAttributeFactory.build()
        attr.survey_attr_id = uuid4()
        build_answer.attrs.append(attr)
        expected_answer = schemas.BaseAnswer.from_orm(build_answer)
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
            factory_answer: Answer,
            factory_survey: Survey,
            build_answer: Answer
    ):
        expected_answer = schemas.BaseAnswer.from_orm(build_answer)
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
            factory_survey: Survey,
            build_answer: Answer
    ):
        expected_answer = schemas.BaseAnswer.from_orm(build_answer)
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


class TestGetAnswer:
    @pytest.mark.parametrize("factory_answers", [True], indirect=True)
    async def test_success(self, session: AsyncSession, admin_user: User, factory_answers: List[Answer]):
        random_answer = random.choice(factory_answers)
        answer = await answer_services.get_answer(session=session, answer_id=random_answer.id, user=admin_user)
        assert random_answer == answer

    @pytest.mark.parametrize("factory_answers", [True], indirect=True)
    async def test_with_not_author(self, session: AsyncSession, factory_answers: List[Answer], user_and_its_pass: dict):
        random_answer = random.choice(factory_answers)
        if random_answer.available:
            answer = await answer_services.get_answer(
                session=session,
                answer_id=random_answer.id,
                user=user_and_its_pass["user"]
            )
            assert random_answer == answer
        else:
            with pytest.raises(HTTPException) as exception:
                await answer_services.get_answer(
                    session=session,
                    answer_id=random_answer.id,
                    user=user_and_its_pass["user"]
                )
                assert exception.value.status_code == 403

    @pytest.mark.parametrize("factory_answers", [True], indirect=True)
    async def test_without_user(self, session: AsyncSession, factory_answers: List[Answer]):
        random_answer = random.choice(factory_answers)
        if random_answer.available:
            answer = await answer_services.get_answer(
                session=session,
                answer_id=random_answer.id,
            )
            assert random_answer == answer
        else:
            with pytest.raises(HTTPException) as exception:
                await answer_services.get_answer(
                    session=session,
                    answer_id=random_answer.id,
                )
                assert exception.value.status_code == 403

    async def test_not_exists_answer(self, session: AsyncSession, admin_user: User):
        with pytest.raises(HTTPException) as exception:
            await answer_services.get_answer(
                session=session,
                answer_id=uuid4(),
                user=admin_user
            )
            assert exception.value.status_code == 404

    async def test_not_exists_answer_and_without_user(self, session: AsyncSession):
        with pytest.raises(HTTPException) as exception:
            await answer_services.get_answer(
                session=session,
                answer_id=uuid4(),
            )
            assert exception.value.status_code == 404
