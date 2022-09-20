import json
import random
from typing import Dict, List
from uuid import uuid4

import pytest
from faker import Faker
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models import User, Survey
from app.schemas.survey import SurveyOut
from tests.factories import UserFactory

fake = Faker()


class TestAddSurvey:
    async def test_with_valid_data(
            self,
            auth_test_client: AsyncClient,
            access_token_and_admin_user: Dict[str, User],
            survey_data: dict
    ):
        response = await auth_test_client.post(
            "/survey",
            json=survey_data,
        )
        assert response.status_code == 201

    async def test_with_invalid_data(
            self,
            auth_test_client: AsyncClient
    ):
        response = await auth_test_client.post("/survey", json={"name": "name", "attrs": [{"name": ""}]})
        assert response.status_code == 422


class TestGetSurvey:
    @pytest.mark.parametrize("factory_surveys", [5], indirect=True)
    async def test_for_exists(self, auth_test_client: AsyncClient, factory_surveys: List[Survey]):
        response = await auth_test_client.get(
            f"/survey/{random.choice(factory_surveys).id}"
        )
        assert response.status_code == 200

    async def test_for_not_exists(self, auth_test_client: AsyncClient):
        response = await auth_test_client.get(f"/survey/{uuid4()}")
        assert response.status_code == 404

    @pytest.mark.parametrize("factory_surveys", [5], indirect=True)
    async def test_for_not_author(self, test_client: AsyncClient, session: AsyncSession, factory_surveys: List[Survey]):
        password = "password"
        user = UserFactory(password=get_password_hash(password))
        session.add(user)
        await session.commit()
        response = await test_client.post(
            "auth/login/access-token",
            data={
                "login": user.username,
                "password": password,
            }
        )
        response_content = json.loads(response.content.decode("utf-8"))
        access_token = response_content.get("access_token")
        response = await test_client.get(
            f"/survey/{random.choice(factory_surveys).id}",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        surveys = json.loads(response.content.decode("utf-8"))
        factory_surveys = [SurveyOut.from_orm(survey).dict() for survey in factory_surveys]
        assert filter(lambda survey: survey["available"] is False, factory_surveys) not in surveys

    @pytest.mark.parametrize("factory_surveys", [5], indirect=True)
    async def test_without_user(self, test_client: AsyncClient, session: AsyncSession, factory_surveys: List[Survey]):
        response = await test_client.get(
            f"/survey/{random.choice(factory_surveys).id}",
        )
        surveys = json.loads(response.content.decode("utf-8"))
        factory_surveys = [SurveyOut.from_orm(survey).dict() for survey in factory_surveys]
        assert filter(lambda survey: survey["available"] is False, factory_surveys) not in surveys


class TestGetSurveys:
    @pytest.mark.parametrize("factory_surveys", [5], indirect=True)
    async def test_for_exists(self, test_client: AsyncClient, factory_surveys: List[Survey]):
        response = await test_client.get("/survey")
        surveys = json.loads(response.content.decode("utf-8"))
        assert surveys

    async def test_for_not_exists(self, test_client: AsyncClient, tables):
        response = await test_client.get("/survey")
        surveys = json.loads(response.content.decode("utf-8"))
        assert not surveys

    @pytest.mark.parametrize("factory_surveys", [5], indirect=True)
    async def test_for_if_available_true(self, test_client: AsyncClient, factory_surveys: List[Survey]):
        response = await test_client.get("/survey?available=true")
        surveys = json.loads(response.content.decode("utf-8"))
        assert all([survey["available"] for survey in surveys])

    @pytest.mark.parametrize("factory_surveys", [5], indirect=True)
    async def test_for_if_available_false(self, test_client: AsyncClient, factory_surveys: List[Survey]):
        response = await test_client.get("/survey?available=false")
        surveys = json.loads(response.content.decode("utf-8"))
        assert not all([survey["available"] for survey in surveys])

    async def test_for_if_available_invalid(self, test_client: AsyncClient):
        response = await test_client.get("/survey?available=not")
        assert response.status_code == 422


class TestUpdateSurvey:
    async def test_for_exists(self, auth_test_client: AsyncClient, factory_surveys: Survey):
        to_update = fake.name()
        response = await auth_test_client.patch(f"/survey/{factory_surveys.id}", json={"name": to_update})
        survey = json.loads(response.content.decode("utf-8"))
        assert survey["name"] == to_update

    async def test_for_not_exists(self, auth_test_client: AsyncClient):
        response = await auth_test_client.patch(f"/survey/{uuid4()}", json={"name": fake.name()})
        assert response.status_code == 404

    async def test_for_not_owner_user(self, test_client: AsyncClient, session: AsyncSession, factory_surveys: Survey):
        user = UserFactory.build()
        session.add(user)
        await session.commit()
        response = await test_client.post(
            "auth/login/access-token",
            data={
                "login": user.username,
                "password": user.password,
            }
        )
        response_content = json.loads(response.content.decode("utf-8"))
        access_token = response_content.get("access_token")
        response = await test_client.patch(
            f"/survey/{factory_surveys.id}",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"name": fake.name()},
        )
        assert response.status_code == 403


class TestUpdateSurveyAttribute:
    async def test_for_exists(self, auth_test_client: AsyncClient, factory_surveys: Survey):
        to_update = fake.text()
        response = await auth_test_client.patch(f"/survey/attr/{factory_surveys.attrs[0].id}", json={"question": to_update})
        survey_attr = json.loads(response.content.decode("utf-8"))
        assert survey_attr["question"] == to_update

    async def test_for_not_exists(self, auth_test_client: AsyncClient):
        response = await auth_test_client.patch(f"/survey/attr/{uuid4()}", json={"question": fake.text()})
        assert response.status_code == 404

    async def test_for_not_owner_user(self, test_client: AsyncClient, session: AsyncSession, factory_surveys: Survey):
        user = UserFactory.build()
        session.add(user)
        await session.commit()
        response = await test_client.post(
            "auth/login/access-token",
            data={
                "login": user.username,
                "password": user.password,
            }
        )
        response_content = json.loads(response.content.decode("utf-8"))
        access_token = response_content.get("access_token")
        response = await test_client.patch(
            f"/survey/attr/{factory_surveys.attrs[0].id}",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"question": fake.text()},
        )
        assert response.status_code == 403
