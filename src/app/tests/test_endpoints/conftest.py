import json

import pytest


@pytest.fixture(scope="function")
def access_token_and_admin_user(test_client, admin_user, admin_user_data) -> dict:
    response = test_client.post(
        "auth/login/access-token",
        json={
            "login": admin_user_data.get("username"),
            "password": admin_user_data.get("password"),
        }
    )
    response_content = json.loads(response.content.decode("utf-8"))
    access_token = response_content.get("access_token")
    return {"access_token": access_token, "admin_user": admin_user}
