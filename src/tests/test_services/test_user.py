from typing import List
from unittest import mock
from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import get_settings
from app.models import User
from app.schemas.user import UserRegistrationIn, UserFilter
from app.services import base as base_services
from app.services import user as user_services
from app.services.filtering.user import search_users

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
    async def test_for_exists_users(self, session: AsyncSession, factory_users: List[User]):
        users = await user_services.get_users(session=session)
        assert len(users) == 5
        
    async def test_for_not_exists_users(self, session: AsyncSession):
        users = await user_services.get_users(session=session)
        assert len(users) == 0


class TestGetUsersWithSearching:
    @pytest.mark.parametrize("factory_users", [5], indirect=True)
    async def test_searching_by_username(self, session: AsyncSession, factory_users: List[User]):
        users = await search_users(session=session, filter=UserFilter(username=factory_users[0].username[:5]))
        assert all([user.username.startswith(factory_users[0].username[:5]) for user in users])

    @pytest.mark.parametrize("factory_users", [5], indirect=True)
    async def test_searching_by_email(self, session: AsyncSession, factory_users: List[User]):
        users = await search_users(session=session, filter=UserFilter(email=factory_users[0].email[:7]))
        assert all([user.email.startswith(factory_users[0].email[:7]) for user in users])

    @pytest.mark.parametrize("factory_users", [5], indirect=True)
    async def test_searching_by_username_and_email(self, session: AsyncSession, factory_users: List[User]):
        users = await search_users(session=session, filter=UserFilter(username=factory_users[0].username[:5], email=factory_users[0].email[:7]))
        assert all([user.username.startswith(factory_users[0].username[:5]) for user in users])
        assert all([user.email.startswith(factory_users[0].email[:7]) for user in users])

    @pytest.mark.parametrize("factory_users", [5], indirect=True)
    async def test_for_not_exists(self, session: AsyncSession, factory_users: List[User]):
        users = await search_users(session=session, filter=UserFilter(username="user"))
        assert not users


class TestDeleteUser:
    async def test_success(self, session: AsyncSession, user_and_its_pass: dict):
        user = await user_services.delete_user(
            session=session,
            login=user_and_its_pass["user"].email,
            password=user_and_its_pass["password"]
        )
        assert user == user_and_its_pass["user"]
        assert not await base_services.is_object_exists(
            session=session,
            statement=select(User).where(User.id == user_and_its_pass["user"].id)
        )

    async def test_404(self, session: AsyncSession):
        with pytest.raises(HTTPException) as exception:
            await user_services.delete_user(
                session=session,
                login="username",
                password="password"
            )
            assert exception.value.status_code == 404

    async def test_wrong_password(self, session: AsyncSession, user_and_its_pass: dict):
        with pytest.raises(HTTPException) as exception:
            await user_services.delete_user(
                session=session,
                login=user_and_its_pass["user"].email,
                password="wrong_password"
            )
            assert exception.value.status_code == 400

    @pytest.mark.parametrize("user_and_its_pass", [{"is_active": False}], indirect=True)
    async def test_not_active_user(self, session: AsyncSession, user_and_its_pass: dict):
        with pytest.raises(HTTPException) as exception:
            await user_services.delete_user(
                session=session,
                login=user_and_its_pass["user"].email,
                password=user_and_its_pass["password"]
            )
            assert exception.value.status_code == 400
