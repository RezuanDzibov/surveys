import json

from user.schemas import UserRetrieve


class TestGetCurrentUser:
    def test_for_exists_user(self, test_client, access_token_and_admin_user):
        response = test_client.get(
            "user/me",
            headers={
                "Authorization": f"Bearer {access_token_and_admin_user.get('access_token')}"
            }
        )
        admin_user = UserRetrieve(**access_token_and_admin_user.get("admin_user"))
        response_user = UserRetrieve(**json.loads(response.content.decode("utf-8")))
        assert response.status_code == 200
        assert admin_user == response_user

    def test_for_invalid_access_token(self, test_client):
        response = test_client.get("user/me", headers={"Authorization": f"Bearer token"})
        assert response.status_code == 403


class TestUpdateCurrentUser:
    def test_for_exists_user(self, test_client, access_token_and_admin_user):
        response = test_client.patch(
            "user/me/update",
            headers={
                "Authorization": f"Bearer {access_token_and_admin_user.get('access_token')}"
            },
            json={
                "first_name": "Another First Name",
                "last_name": "Another Last Name"
            }
        )
        admin_user = access_token_and_admin_user.get("admin_user")
        admin_user["first_name"] = "Another First Name"
        admin_user["last_name"] = "Another Last Name"
        admin_user = UserRetrieve(**admin_user)
        response_user = UserRetrieve(**json.loads(response.content.decode("utf-8")))
        assert response.status_code == 200
        assert admin_user == response_user

    def test_for_invalid_token(self, test_client):
        response = test_client.patch(
            "user/me/update",
            headers={"Authorization": f"Bearer token"},
            json={"username": "some_another_username"}
        )
        assert response.status_code == 403
