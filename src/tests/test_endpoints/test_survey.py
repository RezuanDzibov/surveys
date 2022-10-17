import json
import random
from typing import Dict, List
from uuid import uuid4

import pytest
from faker import Faker
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models import User, Survey, SurveyAttribute
from app.schemas.survey import SurveyOut
from app.services import base as base_services
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
        surveys = json.loads(response.content.decode("utf-8"))["items"]
        assert filter(lambda survey: survey.available is False, [survey.as_dict() for survey in factory_surveys]) not in surveys

    async def test_for_not_exists(self, test_client: AsyncClient, tables):
        response = await test_client.get("/survey")
        surveys = json.loads(response.content.decode("utf-8"))["items"]
        assert not surveys

    @pytest.mark.parametrize("factory_surveys", [5], indirect=True)
    async def test_pagination(self, test_client: AsyncClient, factory_surveys: List[Survey]):
        response = await test_client.get("/survey?size=2")
        surveys = json.loads(response.content.decode("utf-8"))["items"]
        assert len(surveys) == 2


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


class TestGetCurrentUserSurveys:
    @pytest.mark.parametrize("factory_surveys", [5], indirect=True)
    async def test_for_exists(
            self,
            auth_test_client: AsyncClient,
            admin_user: User,
            session: AsyncSession,
            factory_surveys: List[Survey]
    ):
        response = await auth_test_client.get("/survey/user/me")
        surveys = json.loads(response.content.decode("utf-8"))["items"]
        assert all(survey["user_id"] == str(admin_user.id) for survey in surveys)

    async def test_for_not_exists(self, auth_test_client: AsyncClient, admin_user: User, session: AsyncSession):
        response = await auth_test_client.get("/survey/user/me")
        surveys = json.loads(response.content.decode("utf-8"))["items"]
        assert not surveys

    @pytest.mark.parametrize("factory_surveys", [5], indirect=True)
    async def test_if_available_is_true(
            self,
            auth_test_client: AsyncClient,
            admin_user: User,
            session: AsyncSession,
            factory_surveys: List[Survey]
    ):
        response = await auth_test_client.get(
            "/survey/user/me?available=true",
        )
        surveys = json.loads(response.content.decode("utf-8"))["items"]
        assert all(survey["user_id"] == str(admin_user.id) for survey in surveys)
        assert filter(lambda survey: survey["available"] is True, [survey.as_dict() for survey in factory_surveys]) not in surveys

    @pytest.mark.parametrize("factory_surveys", [5], indirect=True)
    async def test_if_available_is_false(
            self,
            auth_test_client: AsyncClient,
            admin_user: User,
            session: AsyncSession,
            factory_surveys: List[Survey]
    ):
        response = await auth_test_client.get(
            "/survey/user/me?available=false",
        )
        surveys = json.loads(response.content.decode("utf-8"))["items"]
        assert all(survey["user_id"] == str(admin_user.id) for survey in surveys)
        assert filter(
            lambda survey: survey["available"] is False, [survey.as_dict() for survey in factory_surveys]
        ) not in surveys

    @pytest.mark.parametrize("factory_surveys", [5], indirect=True)
    async def test_pagination(
            self,
            auth_test_client: AsyncClient,
            admin_user: User,
            session: AsyncSession,
            factory_surveys: List[Survey]
    ):
        response = await auth_test_client.get("/survey/user/me?size=2")
        surveys = json.loads(response.content.decode("utf-8"))["items"]
        assert len(surveys) == 2


class TestGetUserSurveys:
    @pytest.mark.parametrize("factory_surveys", [5], indirect=True)
    async def test_for_exists(
            self,
            test_client: AsyncClient,
            session: AsyncSession,
            admin_user: User,
            factory_surveys: List[Survey]
    ):
        response = await test_client.get(
            f"/survey/user/{admin_user.id}",
        )
        surveys = json.loads(response.content.decode("utf-8"))["items"]
        assert all(survey["user_id"] == str(admin_user.id) for survey in surveys)

    async def test_for_not_exists_user(self, test_client: AsyncClient, session: AsyncSession):
        response = await test_client.get(f"/survey/user/{uuid4()}")
        assert response.status_code == 404

    async def test_for_not_exists_survey(
            self,
            test_client: AsyncClient,
            session: AsyncSession,
            admin_user: User
    ):
        response = await test_client.get(f"/survey/user/{admin_user.id}")
        surveys = json.loads(response.content.decode("utf-8"))["items"]
        assert response.status_code == 200
        assert not surveys


class TestGetUsersWithFiltering:
    @pytest.mark.parametrize("factory_surveys", [5], indirect=True)
    async def test_searching_by_name(self, test_client: AsyncClient, factory_surveys: List[Survey]):
        response = await test_client.get(f"survey/search?name={factory_surveys[0].name[:5]}")
        surveys = json.loads(response.content.decode("utf-8"))["items"]
        assert response.status_code == 200
        assert all([survey["name"].startswith(factory_surveys[0].name[:5]) for survey in surveys])

    @pytest.mark.parametrize("factory_surveys", [5], indirect=True)
    async def test_searching_by_email(self, test_client: AsyncClient, factory_surveys: List[Survey]):
        response = await test_client.get(f"survey/search?description={factory_surveys[0].description[:30]}")
        surveys = json.loads(response.content.decode("utf-8"))["items"]
        assert response.status_code == 200
        assert all([survey["description"].startswith(factory_surveys[0].description[:30]) for survey in surveys])

    @pytest.mark.parametrize("factory_surveys", [5], indirect=True)
    async def test_searching_by_name_and_email(self, test_client: AsyncClient, factory_surveys: List[Survey]):
        response = await test_client.get(f"survey/search?name={factory_surveys[0].name[:5]}&description={factory_surveys[0].description[:30]}")
        surveys = json.loads(response.content.decode("utf-8"))["items"]
        assert response.status_code == 200
        assert all([survey["name"].startswith(factory_surveys[0].name[:5]) for survey in surveys])
        assert all([survey["description"].startswith(factory_surveys[0].description[:30]) for survey in surveys])

    @pytest.mark.parametrize("factory_surveys", [5], indirect=True)
    async def test_for_not_exists_survey(self, test_client: AsyncClient, factory_surveys: List[Survey]):
        response = await test_client.get(f"survey/search?name=name")
        surveys = json.loads(response.content.decode("utf-8"))["items"]
        assert response.status_code == 200
        assert not surveys


class TestDeleteSurvey:
    @pytest.mark.parametrize("factory_surveys", [5], indirect=True)
    async def test_success(self, session: AsyncSession, auth_test_client: AsyncClient, factory_surveys: List[Survey]):
        response = await auth_test_client.delete(
            f"/survey/{factory_surveys[2].id}"
        )
        assert response.status_code == 204
        assert not await base_services.is_object_exists(
            session=session,
            statement=select(Survey).where(Survey.id == factory_surveys[2].id)
        )

    async def test_404(self, auth_test_client: AsyncClient):
        response = await auth_test_client.delete(f"/survey/{uuid4()}")
        assert response.status_code == 404

    @pytest.mark.parametrize("factory_surveys", [5], indirect=True)
    async def test_cascade_deletion(self, session: AsyncSession, auth_test_client, factory_surveys: List[Survey]):
        response = await auth_test_client.delete(
            f"/survey/{factory_surveys[2].id}"
        )
        assert response.status_code == 204
        assert not await base_services.is_object_exists(
            session=session,
            statement=select(SurveyAttribute).where(SurveyAttribute.id == factory_surveys[2].attrs[0].id)
        )

    @pytest.mark.parametrize("factory_surveys", [5], indirect=True)
    async def test_not_author(
            self,
            test_client: AsyncClient,
            factory_surveys: List[Survey],
            access_token_and_user: dict
    ):
        response = await test_client.delete(
            f"/survey/{random.choice(factory_surveys).id}",
            headers={"Authorization": f"Bearer {access_token_and_user['access_token']}"}
        )
        assert response.status_code == 404


class TestDeleteSurveyAttribute:
    @pytest.mark.parametrize("factory_surveys", [5], indirect=True)
    async def test_success(self, session: AsyncSession, auth_test_client: AsyncClient, factory_surveys: List[Survey]):
        attr = factory_surveys[2].attrs[0]
        response = await auth_test_client.delete(f"survey/attr/{attr.id}")
        assert response.status_code == 202
        assert not await base_services.is_object_exists(
            session=session,
            statement=select(SurveyAttribute).where(SurveyAttribute.id == attr.id)
        )

    async def test_404(self, session: AsyncSession, auth_test_client: AsyncClient):
        response = await auth_test_client.delete(f"survey/attr/{uuid4()}")
        assert response.status_code == 404

    @pytest.mark.parametrize("factory_surveys", [5], indirect=True)
    async def test_not_author(
            self,
            session: AsyncSession,
            factory_surveys: List[Survey],
            access_token_and_user: dict,
            auth_test_client: AsyncClient

    ):
        response = await auth_test_client.delete(
            f"/survey/{random.choice(factory_surveys).id}",
            headers={"Authorization": f"Bearer {access_token_and_user['access_token']}"}
        )
        assert response.status_code == 404

