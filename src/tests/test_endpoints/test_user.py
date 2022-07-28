import json

import pytest

from schemas.user import UserRetrieve


class TestGetCurrentUser:
    def test_for_exists_user(self, test_client, access_token_and_admin_user):
        response = test_client.get(
            "users/me",
            headers={
                "Authorization": f"Bearer {access_token_and_admin_user.get('access_token')}"
            }
        )
        admin_user = UserRetrieve.from_orm(access_token_and_admin_user.get("admin_user"))
        response_user = UserRetrieve(**json.loads(response.content.decode("utf-8")))
        assert response.status_code == 200
        assert admin_user == response_user

    def test_for_invalid_access_token(self, test_client):
        response = test_client.get("users/me", headers={"Authorization": f"Bearer token"})
        assert response.status_code == 403


class TestUpdateCurrentUser:
    def test_for_exists_user(self, test_client, access_token_and_admin_user):
        response = test_client.patch(
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

    def test_for_invalid_token(self, test_client):
        response = test_client.patch(
            "users/me/update",
            headers={"Authorization": f"Bearer token"},
            json={"username": "some_another_username"}
        )
        assert response.status_code == 403


class TestGetUsers:
    @pytest.mark.parametrize("factory_users", [5], indirect=True)
    def test_for_exists_users(self, test_client, factory_users):
        response = test_client.get("users")
        users = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 200
        assert len(users) == 5

    def test_for_not_exists_users(self, test_client, tables):
        response = test_client.get("users")
        users = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 200
        assert len(users) == 0
