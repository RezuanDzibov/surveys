import json
import random
from typing import List
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import get_settings
from app.models import Survey, Answer, AnswerAttribute
from app.schemas import survey as schemas
from app.schemas.survey import AnswerRetrieve
from app.services import base as base_services
from tests.factories import AnswerAttributeFactory
from tests.test_endpoints.utils import uuid_to_str, serialize_uuid_to_str

settings = get_settings()


class TestAddAnswer:
    async def test_success(
            self,
            auth_test_client: AsyncClient,
            factory_survey: Survey,
            build_answer: Answer
    ):
        expected_answer = await serialize_uuid_to_str(schemas.BaseAnswer.from_orm(build_answer).dict())
        response = await auth_test_client.post(f"/answer/{factory_survey.id}", json=expected_answer)
        created_answer = json.loads(response.content.decode("utf-8"))
        assert expected_answer == json.loads(json.dumps(schemas.BaseAnswer(**created_answer).dict(), default=uuid_to_str))

    async def test_not_exist_survey_attr(
            self,
            auth_test_client: AsyncClient,
            factory_survey: Survey,
            build_answer: Answer

    ):
        attr = AnswerAttributeFactory.build()
        attr.survey_attr_id = uuid4()
        build_answer.attrs.append(attr)
        answer = await serialize_uuid_to_str(schemas.BaseAnswer.from_orm(build_answer).dict())
        response = await auth_test_client.post(f"/answer/{factory_survey.id}", json=answer)
        assert response.status_code == 404

    async def test_user_already_created_answer_for_survey(
            self,
            auth_test_client: AsyncClient,
            factory_survey: Survey,
            factory_answer: Answer,
            build_answer: Answer
    ):
        answer = await serialize_uuid_to_str(schemas.BaseAnswer.from_orm(build_answer).dict())
        response = await auth_test_client.post(f"/answer/{factory_answer.survey_id}", json=answer)
        assert response.status_code == 409

    async def test_not_exists_survey(
            self,
            auth_test_client: AsyncClient,
            factory_survey: Survey,
            build_answer: Answer
    ):
        answer = await serialize_uuid_to_str(schemas.BaseAnswer.from_orm(build_answer).dict())
        response = await auth_test_client.post(f"/answer/{uuid4()}", json=answer)
        assert response.status_code == 404

    async def test_without_user(
            self,
            factory_survey: Survey,
            test_client: AsyncClient,
            build_answer: Answer
    ):
        answer = await serialize_uuid_to_str(schemas.BaseAnswer.from_orm(build_answer).dict())
        response = await test_client.post(f"/answer/{factory_survey.id}", json=answer)
        assert response.status_code == 401


class TestDeleteAnswer:
    @pytest.mark.parametrize("factory_answer", [True], indirect=True)
    async def test_success(self, session: AsyncSession, auth_test_client: AsyncClient, factory_answer: Answer):
        response = await auth_test_client.delete(f"/answer/{factory_answer.id}")
        assert response.status_code == 204
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

    async def test_404(self, session: AsyncSession, auth_test_client):
        response = await auth_test_client.delete(f"/answer/{uuid4()}")
        assert response.status_code == 404

    @pytest.mark.parametrize("factory_answer", [True], indirect=True)
    async def test_for_not_author(self, factory_answer: Answer, user_auth_test_client: AsyncClient, ):
        response = await user_auth_test_client.delete(f"/answer/{factory_answer.id}")
        assert response.status_code == 403


class TestGetAnswer:
    @pytest.mark.parametrize("factory_answers", [True], indirect=True)
    async def test_success(self, session: AsyncSession, auth_test_client: AsyncClient, factory_answers: List[Answer]):
        random_answer = random.choice(factory_answers)
        response = await auth_test_client.get(f"/answer/{random_answer.id}")
        answer = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 200
        assert answer == await serialize_uuid_to_str(AnswerRetrieve.from_orm(random_answer).dict())

    @pytest.mark.parametrize("factory_answers", [True], indirect=True)
    async def test_with_not_author(
            self,
            factory_answers: List[Answer],
            user_auth_test_client: AsyncClient
    ):
        random_answer = random.choice(factory_answers)
        response = await user_auth_test_client.get(f"/answer/{random_answer.id}")
        if random_answer.available:
            answer = json.loads(response.content.decode("utf-8"))
            assert response.status_code == 200
            assert answer == await serialize_uuid_to_str(AnswerRetrieve.from_orm(random_answer).dict())
        else:
            assert response.status_code == 403

    @pytest.mark.parametrize("factory_answers", [True], indirect=True)
    async def test_without_user(
            self,
            session: AsyncSession,
            factory_answers: List[Answer],
            test_client: AsyncClient
    ):
        random_answer = random.choice(factory_answers)
        response = await test_client.get(f"/answer/{random_answer.id}")
        if random_answer.available:
            answer = json.loads(response.content.decode("utf-8"))
            assert response.status_code == 200
            assert answer == await serialize_uuid_to_str(AnswerRetrieve.from_orm(random_answer).dict())
        else:
            assert response.status_code == 403

    async def test_not_exists_answer(self, session: AsyncSession, auth_test_client: AsyncClient):
        response = await auth_test_client.get(f"/answer/{uuid4()}")
        assert response.status_code == 404

    async def test_not_exists_answer_and_without_user(self, session: AsyncSession, test_client: AsyncClient):
        response = await test_client.get(f"/answer/{uuid4()}")
        assert response.status_code == 404
