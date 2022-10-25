import json
from typing import List
from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.core.settings import get_settings
from app.models import AnswerAttribute, Survey, Answer, User
from app.schemas import survey as schemas

settings = get_settings()


class TestAddAnswer:
    @pytest.mark.parametrize("build_answer_attrs", [3], indirect=True)
    async def test_success(
            self,
            auth_test_client: AsyncClient,
            build_answer_attrs: List[AnswerAttribute],
            factory_survey: Survey

    ):
        expected_answer = schemas.BaseAnswer(attrs=[attr.as_dict() for attr in build_answer_attrs])
        response = await auth_test_client.post(f"/answer/{factory_survey.id}", json=expected_answer.dict())
        created_answer = json.loads(response.content.decode("utf-8"))
        assert expected_answer == schemas.BaseAnswer(**created_answer)

    async def test_409(
            self,
            auth_test_client: AsyncClient,
            build_answer_attrs: List[AnswerAttribute],
            factory_answer: Answer
    ):
        answer = schemas.BaseAnswer(attrs=[attr.as_dict() for attr in build_answer_attrs])
        response = await auth_test_client.post(f"/answer/{factory_answer.survey_id}", json=answer.dict())
        assert response.status_code == 409

    async def test_not_exists_survey(
            self,
            auth_test_client: AsyncClient,
            build_answer_attrs: List[AnswerAttribute],
    ):
        answer = schemas.BaseAnswer(attrs=[attr.as_dict() for attr in build_answer_attrs])
        response = await auth_test_client.post(f"/answer/{uuid4()}", json=answer.dict())
        assert response.status_code == 404

    @pytest.mark.parametrize("admin_user", [{"is_active": False}], indirect=True)
    async def test_for_inactive_user(self, tables, admin_user: User, test_client: AsyncClient):
        response = await test_client.post(
            "auth/login/access-token",
            data={
                "login": admin_user.username,
                "password": settings.ADMIN_FIXTURE_PASSWORD,
            }
        )
        assert response.status_code == 400

    async def test_without_user(
            self,
            factory_survey: Survey,
            test_client: AsyncClient,
            build_answer_attrs: List[AnswerAttribute]
    ):
        answer = schemas.BaseAnswer(attrs=[attr.as_dict() for attr in build_answer_attrs])
        response = await test_client.post(f"/answer/{factory_survey.id}", json=answer.dict())
        assert response.status_code == 401
