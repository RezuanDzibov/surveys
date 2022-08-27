from typing import Dict

from httpx import AsyncClient

from models import User


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
