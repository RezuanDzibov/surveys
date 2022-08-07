from copy import copy

import pytest
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.settings import get_settings
from models import User
from services import base as base_services

settings = get_settings()


class TestGetObject:
    async def test_get_object(self, session: AsyncSession, admin_user: User):
        statement = select(User).where(User.id == admin_user.id)
        object_in_db = await base_services.get_object(session=session, statement=statement, model=User)
        assert admin_user == object_in_db

    async def test_get_object_id_as_str(self, session: AsyncSession, admin_user: User):
        statement = select(User).where(User.id == str(admin_user.id))
        object_in_db = await base_services.get_object(session=session, statement=statement, model=User)
        assert admin_user == object_in_db

    async def test_get_not_exists_object(self, session: AsyncSession):
        statement = select(User).where(User.username == "username")
        with pytest.raises(HTTPException) as exception_info:
            await base_services.get_object(session=session, statement=statement, model=User)
            assert exception_info.value.status_code == 404


class TestIsObjectExists:
    async def test_exists_object(self, session: AsyncSession, admin_user: User):
        statement = select(User).where(User.username == admin_user.username)
        assert await base_services.is_object_exists(session=session, statement=statement)

    async def test_not_exists_object(self, session):
        statement = select(User).where(User.username == "some username")
        assert not await base_services.is_object_exists(session=session, statement=statement)


class TestUpdateObject:
    async def test_exists_object(self, session: AsyncSession, admin_user: User):
        expected_object = copy(admin_user)
        expected_object.username = "username"
        object_in_db = await base_services.update_object(
            session=session,
            model=User,
            where_statements=[User.username == admin_user.username],
            to_update={"username": "username"},
        )
        assert expected_object == object_in_db

    async def test_not_exists_object(self, session: AsyncSession):
        with pytest.raises(HTTPException) as exception_info:
            await base_services.update_object(
                session=session,
                model=User,
                where_statements=[User.username == "username"],
                to_update={"username": "username_1"}
            )
            assert exception_info.value.status_code == 404


class TestInsertObject:
    async def test_not_exists_object(self, session: AsyncSession, admin_user_data: dict):
        inserted_object = await base_services.insert_object(
            session=session,
            model=User,
            to_insert=admin_user_data,
        )
        assert inserted_object

    async def test_exists_object(self, session: AsyncSession, admin_user: User, admin_user_data: dict):
        with pytest.raises(HTTPException) as exception_info:
            await base_services.insert_object(
                session=session,
                model=User,
                to_insert=admin_user_data,
            )
            assert exception_info.value.status_code == 409


class TestDeleteObject:
    async def test_exists_object(self, session: AsyncSession, admin_user: User):
        deleted_object = await base_services.delete_object(
            session=session,
            model=User,
            where_statements=[User.username == admin_user.username],
        )
        assert admin_user == deleted_object
        assert not await base_services.is_object_exists(session=session, statement=User.id == admin_user.id)

    async def test_not_exists_object(self, session: AsyncSession):
        with pytest.raises(HTTPException) as exception_info:
            await base_services.delete_object(
                session=session,
                model=User,
                where_statements=[User.username == "some_username"],
            )
        assert exception_info.value.status_code == 404


class TestGetObjects:
    async def test_for_exist_objects(self, session: AsyncSession, admin_user: User):
        objects = await base_services.get_objects(session=session, model=User)
        assert objects == [admin_user]

    async def test_for_not_exists_objects(self, session: AsyncSession):
        objects = await base_services.get_objects(session=session, model=User)
        assert objects == []
