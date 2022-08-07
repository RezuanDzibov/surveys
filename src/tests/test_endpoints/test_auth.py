import json

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from core.settings import get_settings
from models import User
from services import auth as auth_services

settings = get_settings()


class TestUserRegistration:
    async def test_for_not_exists_user(self, tables, admin_user_data: dict, test_client: AsyncClient):
        admin_user_data["password_repeat"] = settings.ADMIN_FIXTURE_PASSWORD
        admin_user_data = json.loads(json.dumps(admin_user_data, default=str))
        response = await test_client.post("auth/registration", json=admin_user_data)
        assert response.status_code == 200

    async def test_for_exists_user(self, tables, admin_user: User, admin_user_data: dict, test_client: AsyncClient):
        admin_user_data["password_repeat"] = settings.ADMIN_FIXTURE_PASSWORD
        admin_user_data = json.loads(json.dumps(admin_user_data, default=str))
        response = await test_client.post("auth/registration", json=admin_user_data)
        assert response.status_code == 409

    async def test_for_invalid_data(self, tables, admin_user_data: dict, test_client: AsyncClient):
        admin_user_data["password"] = "non"
        admin_user_data = json.loads(json.dumps(admin_user_data, default=str))
        response = await test_client.post("auth/registration", json=admin_user_data)
        assert response.status_code == 422

    async def test_for_not_match_password_and_password_repeat(
            self,
            tables,
            admin_user_data: dict,
            test_client: AsyncClient
    ):
        admin_user_data["password_repeat"] = "not_match_password"
        admin_user_data = json.loads(json.dumps(admin_user_data, default=str))
        response = await test_client.post("auth/registration", json=admin_user_data)
        assert response.status_code == 400


class TestUserAccessToken:
    async def test_for_exists_user(self, tables, admin_user: User, admin_user_data: dict, test_client: AsyncClient):
        response = await test_client.post(
            "auth/login/access-token",
            json={
                "login": admin_user_data.get("username"),
                "password": admin_user_data.get("password"),
            }
        )
        assert response.status_code == 200

    @pytest.mark.parametrize("admin_user", [{"is_active": False}], indirect=True)
    async def test_for_inactive_user(self, tables, admin_user: User, test_client: AsyncClient):
        response = await test_client.post(
            "auth/login/access-token",
            json={
                "login": admin_user.username,
                "password": settings.ADMIN_FIXTURE_PASSWORD,
            }
        )
        assert response.status_code == 400

    async def test_for_not_exists_user(self, tables, test_client: AsyncClient):
        response = await test_client.post(
            "auth/login/access-token",
            json={
                "login": "username",
                "password": "password",
            }
        )
        assert response.status_code == 404


class TestConfirmEmail:
    @pytest.mark.parametrize("admin_user", [{"is_active": False}], indirect=True)
    async def test_for_exists_user(self, tables, admin_user: User, session: AsyncSession, test_client: AsyncClient):
        verification = await auth_services.create_verification(
            session=session,
            user_id=str(admin_user.id),
        )
        response = await test_client.get(
            f"auth/confirm-registration/{verification.id}"
        )
        assert response.status_code == 200


class TestRecoverPassword:
    def test_for_exists_user(self, admin_user, test_client):
        response = test_client.get(f"auth/recover-password/{admin_user.email}")
        assert response.status_code == 200

    def test_for_not_exists_user(self, tables, test_client):
        response = test_client.get("auth/password-recovery/email@gmail.com")
        assert response.status_code == 404


class TestResetPassword:
    def test_for_exists_user(self, admin_user, session, task, test_client):
        reset_token = auth_services.recover_password(
            session=session,
            task=task,
            email=admin_user.email,
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
            email=admin_user.email,
        )
        response = test_client.post("auth/reset-password", json={"reset_token": reset_token, "new_password": "password"})
        assert response.status_code == 400
