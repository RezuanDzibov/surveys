import json
import random
from typing import Dict, List
from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.models import User, Survey


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
