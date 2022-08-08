import json
import uuid
from typing import List

import pytest
from httpx import AsyncClient

from models import User
from schemas.user import UserRetrieve


class TestGetCurrentUser:
    async def test_for_exists_user(self, test_client: AsyncClient, access_token_and_admin_user: dict):
        response = await test_client.get(
            "users/me",
            headers={
                "Authorization": f"Bearer {access_token_and_admin_user.get('access_token')}"
            }
        )
        admin_user = UserRetrieve.from_orm(access_token_and_admin_user.get("admin_user"))
        response_user = UserRetrieve(**json.loads(response.content.decode("utf-8")))
        assert response.status_code == 200
        assert admin_user == response_user

    async def test_for_invalid_access_token(self, test_client: AsyncClient):
        response = await test_client.get("users/me", headers={"Authorization": f"Bearer token"})
        assert response.status_code == 403


class TestUpdateCurrentUser:
    async def test_for_exists_user(self, test_client: AsyncClient, access_token_and_admin_user: dict):
        response = await test_client.patch(
            "users/me/update",
            headers={
                "Authorization": f"Bearer {access_token_and_admin_user.get('access_token')}"
            },
            json={
                "first_name": "Another First Name",
                "last_name": "Another Last Name"
            }
        )
        admin_user = access_token_and_admin_user.get("admin_user")
        admin_user.first_name = "Another First Name"
        admin_user.last_name = "Another Last Name"
        admin_user = UserRetrieve.from_orm(admin_user)
        response_user = UserRetrieve(**json.loads(response.content.decode("utf-8")))
        assert response.status_code == 200
        assert admin_user == response_user

    async def test_for_invalid_token(self, test_client: AsyncClient):
        response = await test_client.patch(
            "users/me/update",
            headers={"Authorization": f"Bearer token"},
            json={"username": "some_another_username"}
        )
        assert response.status_code == 403


class TestGetUsers:
    @pytest.mark.parametrize("factory_users", [5], indirect=True)
    async def test_for_exists_users(self, test_client: AsyncClient, factory_users: List[User]):
        response = await test_client.get("users")
        users = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 200
        assert len(users) == 5

    async def test_for_not_exists_users(self, test_client: AsyncClient, tables):
        response = await test_client.get("users")
        users = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 200
        assert len(users) == 0


class TestGetUser:
    @pytest.mark.parametrize("factory_users", [5], indirect=True)
    async def test_for_exists_user(
            self,
            test_client: AsyncClient,
            admin_user: User,
            factory_users: List[User],
            access_token_and_admin_user
    ):
        response = await test_client.get(f"users/{admin_user.id}")
        admin_user = UserRetrieve.from_orm(admin_user)
        response_user = UserRetrieve(**json.loads(response.content.decode("utf-8")))
        assert response.status_code == 200
        assert admin_user == response_user

    @pytest.mark.parametrize("factory_users", [5], indirect=True)
    async def test_for_not_exists_user(self, test_client: AsyncClient, factory_users: List[User]):
        response = await test_client.get(f"users/{uuid.uuid4()}")
        assert response.status_code == 404
