from unittest import mock
from uuid import uuid4

import pytest
from asyncpg import ForeignKeyViolationError
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_password
from app.models import Verification, User
from app.services import auth as auth_services
from app.services import base as base_services


class TestAuthenticate:
    async def test_for_exists_user_by_username(self, session: AsyncSession, admin_user: User, admin_user_data: dict):
        user_in_db = await auth_services.authenticate(
            session=session,
            login=admin_user.username,
            password=admin_user_data.get("password"),
        )
        assert admin_user == user_in_db

    async def test_for_exists_user_by_email(self, session: AsyncSession, admin_user: User, admin_user_data: dict):
        user_in_db = await auth_services.authenticate(
            session=session,
            login=admin_user.email,
            password=admin_user_data.get("password"),
        )
        assert admin_user == user_in_db

    async def test_for_not_exists_user_by_username(self, session: AsyncSession):
        with pytest.raises(HTTPException) as exception_info:
            await auth_services.authenticate(
                session=session,
                login="username",
                password="password",
            )
            assert exception_info.value.status_code == 404

    async def test_for_not_exists_user_by_email(self, session: AsyncSession):
        with pytest.raises(HTTPException) as exception_info:
            await auth_services.authenticate(
                session=session,
                login="eamil@gmail.com",
                password="password",
            )
            assert exception_info.value.status_code == 404

    async def test_for_invalid_password_by_username(self, session: AsyncSession, admin_user: User):
        with pytest.raises(HTTPException) as exception_info:
            await auth_services.authenticate(
                session=session,
                login=admin_user.username,
                password="password"
            )
            assert exception_info.value.status_code == 400

    async def test_for_invalid_password_by_email(self, session: AsyncSession, admin_user: User):
        with pytest.raises(HTTPException) as exception_info:
            await auth_services.authenticate(
                session=session,
                login=admin_user.email,
                password="password"
            )
            assert exception_info.value.status_code == 400


class TestCreateVerification:
    async def test_for_exists_user(self, session: AsyncSession, admin_user: User):
        verification = await auth_services.create_verification(
            session=session,
            user_id=str(admin_user.id)
        )
        assert verification

    async def test_for_not_exists_user(self, session: AsyncSession):
        with pytest.raises(ForeignKeyViolationError):
            await auth_services.create_verification(
                session=session,
                user_id=str(uuid4())
            )


class TestVerifyRegistrationUser:
    async def test_for_exists_verification(self, session: AsyncSession, admin_user: User):
        verification = await auth_services.create_verification(
            session=session,
            user_id=str(admin_user.id),
        )
        await auth_services.verify_registration_user(
            session=session,
            verification_id=verification.id,
        )
        statement = select(Verification).where(Verification.id == verification.id)
        assert not await base_services.is_object_exists(
            session=session,
            statement=statement,
        )

    async def test_for_not_exists_verification(self, session):
        with pytest.raises(HTTPException) as exception_info:
            await auth_services.verify_registration_user(
                session=session,
                verification_id=str(uuid4())
            )
            assert exception_info.value.status_code == 404


class TestVerifyPasswordResetToken:
    async def test_for_valid_reset_token(self, session: AsyncSession, admin_user: User, task: mock.Mock):
        reset_token = await auth_services.recover_password(
            session=session,
            task=task,
            email=admin_user.email,
        )
        email = auth_services.verify_password_reset_token(token=reset_token)
        assert email == admin_user.email

    def test_for_invalid_reset_token(self):
        email = auth_services.verify_password_reset_token(token="some_token")
        assert not email


class TestRecoverPassword:
    async def test_for_exists_user(self, session: AsyncSession, task: mock.Mock, admin_user: User):
        reset_token = await auth_services.recover_password(
            session=session,
            task=task,
            email=admin_user.email,
        )
        assert auth_services.verify_password_reset_token(token=reset_token)

    async def test_for_not_exists_user(self, session: AsyncSession, task: mock.Mock):
        with pytest.raises(HTTPException) as exception_info:
            await auth_services.recover_password(
                session=session,
                task=task,
                email="some_email@gmail.com",
            )
            assert exception_info.value.status_code == 404


class TestResetPassword:
    async def test_for_valid_reset_token(self, session: AsyncSession, task: mock.Mock, admin_user: User):
        reset_token = await auth_services.recover_password(
            session=session,
            task=task,
            email=admin_user.email,
        )
        updated_user = await auth_services.reset_password(
            session=session,
            token=reset_token,
            new_password="some_new_pass"
        )
        assert verify_password("some_new_pass", updated_user.password)

    async def test_for_invalid_reset_token(self, session: AsyncSession):
        with pytest.raises(HTTPException) as exception_info:
            await auth_services.reset_password(
                session=session,
                token="token",
                new_password="password"
            )
        assert exception_info.value.status_code == 400

    async def test_for_inactive_user(self, session: AsyncSession, task: mock.Mock, admin_user_data: dict):
        admin_user_data["is_active"] = False
        await base_services.insert_object(
            session=session,
            model=User,
            to_insert=admin_user_data,
            return_object=False
        )
        reset_token = await auth_services.recover_password(
            session=session,
            task=task,
            email=admin_user_data.get("email"),
        )
        with pytest.raises(HTTPException) as exception_info:
            await auth_services.reset_password(
                session=session,
                token=reset_token,
                new_password="some_new_pass"
            )
            assert exception_info.value.status_code == 400
