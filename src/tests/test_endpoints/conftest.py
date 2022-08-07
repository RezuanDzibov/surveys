import json

import pytest
from httpx import AsyncClient

from models import User


@pytest.fixture(scope="function")
async def access_token_and_admin_user(test_client: AsyncClient, admin_user: User, admin_user_data: dict) -> dict:
    response = await test_client.post(
        "auth/login/access-token",
        json={
            "login": admin_user_data.get("username"),
            "password": admin_user_data.get("password"),
        }
    )
    response_content = json.loads(response.content.decode("utf-8"))
    access_token = response_content.get("access_token")
    return {"access_token": access_token, "admin_user": admin_user}
