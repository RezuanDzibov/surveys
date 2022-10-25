from typing import List
from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AnswerAttribute, User, Survey, Answer
from app.schemas import survey as schemas
from app.services import survey as survey_services


class TestCreateAnswer:
    @pytest.mark.parametrize("build_answer_attrs", [3], indirect=True)
    async def test_success(
            self,
            admin_user: User,
            session: AsyncSession,
            build_answer_attrs: List[AnswerAttribute],
            factory_survey: Survey
    ):
        expected_answer = schemas.BaseAnswer(attrs=[attr.as_dict() for attr in build_answer_attrs])
        created_answer = await survey_services.create_answer(
            session=session,
            answer=expected_answer,
            user_id=admin_user.id,
            survey_id=factory_survey.id
        )
        assert expected_answer == schemas.BaseAnswer.from_orm(created_answer)

    async def test_409(
            self,
            admin_user: User,
            session: AsyncSession,
            build_answer_attrs: List[AnswerAttribute],
            factory_answer: Answer
    ):
        answer = schemas.BaseAnswer(attrs=[attr.as_dict() for attr in build_answer_attrs])
        with pytest.raises(HTTPException) as exception:
            await survey_services.create_answer(
                session=session,
                answer=answer,
                user_id=admin_user.id,
                survey_id=factory_answer.survey_id
            )
            assert exception.value.status_code == 409

    async def test_not_exists_survey(
            self,
            admin_user: User,
            session: AsyncSession,
            build_answer_attrs: List[AnswerAttribute],
            factory_answer: Answer
    ):
        answer = schemas.BaseAnswer(attrs=[attr.as_dict() for attr in build_answer_attrs])
        with pytest.raises(HTTPException) as exception:
            await survey_services.create_answer(
                session=session,
                answer=answer,
                user_id=admin_user.id,
                survey_id=uuid4()
            )
            assert exception.value.status_code == 404


class TestCreateAnswerAttributes:
    @pytest.mark.parametrize("factory_answer", [False], indirect=True)
    async def test_success(
            self,
            session: AsyncSession,
            factory_answer: Answer,
            build_answer_attrs: List[AnswerAttribute]
    ):
        expected_attrs = [schemas.AnswerAttribute.from_orm(attr) for attr in build_answer_attrs]
        created_attrs = await survey_services.create_answer_attrs(
            session=session,
            attrs=expected_attrs,
            answer_id=factory_answer.id
        )
        assert expected_attrs == [schemas.AnswerAttribute.from_orm(attr) for attr in created_attrs]

