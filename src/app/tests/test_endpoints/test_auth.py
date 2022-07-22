import pytest

from auth import services as auth_services
from settings import get_settings

settings = get_settings()


class TestUserRegistration:
    def test_for_not_exists_user(self, tables, admin_user_data, test_client):
        response = test_client.post("auth/registration", json=admin_user_data)
        assert response.status_code == 200

    def test_for_exists_user(self, tables, admin_user, admin_user_data, test_client):
        response = test_client.post("auth/registration", json=admin_user_data)
        assert response.status_code == 409

    def test_for_invalid_data(self, tables, admin_user_data, test_client):
        admin_user_data["password"] = "non"
        response = test_client.post("auth/registration", json=admin_user_data)
        assert response.status_code == 422


class TestUserAccessToken:
    def test_for_exists_user(self, tables, admin_user, admin_user_data, test_client):
        response = test_client.post(
            "auth/login/access-token",
            json={
                "login": admin_user_data.get("username"),
                "password": admin_user_data.get("password"),
            }
        )
        assert response.status_code == 200

    @pytest.mark.parametrize("admin_user", [{"is_active": False}], indirect=True)
    def test_for_inactive_user(self, tables, admin_user, test_client):
        response = test_client.post(
            "auth/login/access-token",
            json={
                "login": admin_user.get("username"),
                "password": settings.ADMIN_FIXTURE_PASSWORD,
            }
        )
        assert response.status_code == 400

    def test_for_not_exists_user(self, tables, test_client):
        response = test_client.post(
            "auth/login/access-token",
            json={
                "login": "username",
                "password": "password",
            }
        )
        assert response.status_code == 404


class TestConfirmEmail:
    @pytest.mark.parametrize("admin_user", [{"is_active": False}], indirect=True)
    def test_for_exists_user(self, tables, admin_user, session, test_client):
        verification = auth_services.create_verification(
            session=session,
            user_id=str(admin_user.get("id")),
        )
        response = test_client.get(
            f"auth/confirm-registration/{verification.get('id')}"
        )
        assert response.status_code == 200


class TestRecoverPassword:
    def test_for_exists_user(self, admin_user, test_client):
        response = test_client.get(f"auth/recover-password/{admin_user.get('email')}")
        assert response.status_code == 200

    def test_for_not_exists_user(self, tables, test_client):
        response = test_client.get("auth/password-recovery/email@gmail.com")
        assert response.status_code == 404


class TestResetPassword:
    def test_for_exists_user(self, admin_user, session, task, test_client):
        reset_token = auth_services.recover_password(
            session=session,
            task=task,
            email=admin_user.get("email"),
        )
        response = test_client.post("auth/reset-password", json={"reset_token": reset_token, "new_password": "password"})
        assert response.status_code == 200

    def test_for_invalid_token(self, test_client):
        response = test_client.post("auth/reset-password", json={"reset_token": "some_token", "new_password": "password"})
        assert response.status_code == 400

    @pytest.mark.parametrize("admin_user", [{"is_active": False}], indirect=True)
    def test_for_inactive_user(self, admin_user, task, session, test_client):
        reset_token = auth_services.recover_password(
            session=session,
            task=task,
            email=admin_user.get("email"),
        )
        response = test_client.post("auth/reset-password", json={"reset_token": reset_token, "new_password": "password"})
        assert response.status_code == 400
