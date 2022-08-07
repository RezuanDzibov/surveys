from unittest import mock
from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.settings import get_settings
from models import User
from schemas.user import UserRegistrationIn
from services import user as user_services

settings = get_settings()


class TestCreateUser:
    async def test_create_user(self, session: AsyncSession, admin_user_data: dict, task: mock.Mock):
        admin_user_data["password_repeat"] = settings.ADMIN_FIXTURE_PASSWORD
        user_to_insert = UserRegistrationIn(**admin_user_data)
        user = await user_services.create_user(
            session=session,
            new_user=user_to_insert,
            task=task,
        )
        assert user

    async def test_create_user_with_exists_username(
            self,
            session: AsyncSession,
            admin_user: User,
            admin_user_data: dict,
            task: mock.Mock
    ):
        admin_user_data["password_repeat"] = settings.ADMIN_FIXTURE_PASSWORD
        admin_user_data["email"] = "someanotheremail@gmail.com"
        user_to_insert = UserRegistrationIn(**admin_user_data)
        with pytest.raises(HTTPException) as exception_info:
            await user_services.create_user(
                session=session,
                new_user=user_to_insert,
                task=task,
            )
        assert exception_info.value.status_code == 409

    async def test_create_user_with_exists_email(
            self,
            session: AsyncSession,
            admin_user: User,
            admin_user_data: dict,
            task: mock.Mock
    ):
        admin_user_data["password_repeat"] = settings.ADMIN_FIXTURE_PASSWORD
        admin_user_data["username"] = "username"
        user_to_insert = UserRegistrationIn(**admin_user_data)
        with pytest.raises(HTTPException) as exception_info:
            await user_services.create_user(
                session=session,
                new_user=user_to_insert,
                task=task,
            )
        assert exception_info.value.status_code == 409


class TestGetUser:
    async def test_exists_user_search_by_id(self, session: AsyncSession, admin_user: User):
        user = await user_services.get_user(session=session, where_statements=[User.id == admin_user.id])
        assert user == admin_user

    async def test_exists_user_search_by_username(self, session: AsyncSession, admin_user: User):
        user = await user_services.get_user(session=session, where_statements=[User.username == admin_user.username])
        assert user == admin_user

    async def test_exists_user_search_by_email(self, session: AsyncSession, admin_user: User):
        user = await user_services.get_user(session=session, where_statements=[User.email == admin_user.email])
        assert user == admin_user

    async def test_not_exists_search_by_id(self, session: AsyncSession):
        with pytest.raises(HTTPException) as exception_info:
            await user_services.get_user(session=session, where_statements=[User.id == uuid4()])
            assert exception_info.value.status_code == 404

    async def test_not_exists_search_by_username(self, session: AsyncSession):
        with pytest.raises(HTTPException) as exception_info:
            await user_services.get_user(session=session, where_statements=[User.username == "some username"])
            assert exception_info.value.status_code == 404

    async def test_not_exists_search_by_email(self, session: AsyncSession):
        with pytest.raises(HTTPException) as exception_info:
            await user_services.get_user(session=session, where_statements=[User.email == "someemail@gmail.com"])
            assert exception_info.value.status_code == 404


class TestUpdateUser:
    async def test_update_exists_user(self, session: AsyncSession, admin_user: User):
        admin_user.username = "username"
        user_in_db = await user_services.update_user(
            session=session,
            where_statements=[User.id == admin_user.id],
            to_update={"username": "username"},
        )
        assert admin_user == user_in_db

    async def test_update_not_exists_object(self, session: AsyncSession):
        with pytest.raises(HTTPException) as exception_info:
            await user_services.update_user(
                session=session,
                to_update={"username": "some"},
                where_statements=[User.username == "some0"],
            )
            assert exception_info.value.status_code == 404


class TestGetUsers:
    @pytest.mark.parametrize("factory_users", [5], indirect=True)
    def test_for_exists_users(self, session, factory_users):
        users = user_services.get_users(session=session)
        assert len(users) == 5

    def test_for_not_exists_users(self, session):
        users = user_services.get_users(session=session)
        assert len(users) == 0
