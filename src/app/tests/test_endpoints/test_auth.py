from auth import services as auth_services
from auth.security import get_password_hash
from initial_data_fixtures import create_admin_user


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

    def test_for_inactive_user(self, tables, admin_user_data, test_client):
        admin_user_data["is_active"] = False
        admin_user_data["password"] = get_password_hash(admin_user_data.get("password"))
        create_admin_user(to_insert=admin_user_data)
        response = test_client.post(
            "auth/login/access-token",
            json={
                "login": admin_user_data.get("username"),
                "password": admin_user_data.get("password"),
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
    def test_for_exists_user(self, tables, admin_user_data, db_session, test_client):
        admin_user_data["is_active"] = False
        user = create_admin_user(to_insert=admin_user_data)
        verification = auth_services.create_verification(
            session=db_session,
            user_id=str(user.get("id")),
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
    def test_for_exists_user(self, admin_user, db_session, task, test_client):
        reset_token = auth_services.recover_password(
            session=db_session,
            task=task,
            email=admin_user.get("email"),
        )
        response = test_client.post("auth/reset-password", json={"token": reset_token, "new_password": "password"})
        assert response.status_code == 200

    def test_for_invalid_token(self, test_client):
        response = test_client.post("auth/reset-password", json={"token": "some_token", "new_password": "password"})
        assert response.status_code == 400

    def test_for_inactive_user(self, tables, admin_user_data, task, db_session, test_client):
        admin_user_data["is_active"] = False
        create_admin_user(to_insert=admin_user_data)
        reset_token = auth_services.recover_password(
            session=db_session,
            task=task,
            email=admin_user_data.get("email"),
        )
        response = test_client.post("auth/reset-password", json={"token": reset_token, "new_password": "password"})
        assert response.status_code == 400
