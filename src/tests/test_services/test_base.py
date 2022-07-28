from copy import copy

import pytest
from fastapi import HTTPException
from sqlalchemy import select

from app.core.settings import get_settings
from app.models import User
from app.services import base as base_services

settings = get_settings()


class TestGetObject:
    def test_get_object(self, session, admin_user):
        statement = select(User).where(User.id == admin_user.id)
        object_in_db = base_services.get_object(session=session, statement=statement, model=User)
        assert admin_user == object_in_db

    def test_get_object_id_as_str(self, session, admin_user):
        statement = select(User).where(User.id == str(admin_user.id))
        object_in_db = base_services.get_object(session=session, statement=statement, model=User)
        assert admin_user == object_in_db

    def test_get_not_exists_object(self, session):
        with pytest.raises(HTTPException) as exception_info:
            statement = select(User).where(User.username == "someusername")
            base_services.get_object(session=session, statement=statement, model=User)
            assert exception_info.value.status_code == 404


class TestIsObjectExists:
    def test_exists_object(self, session, admin_user):
        statement = select(User).where(User.username == admin_user.username)
        assert base_services.is_object_exists(session=session, statement=statement)

    def test_not_exists_object(self, session):
        statement = select(User).where(User.username == "some username")
        assert not base_services.is_object_exists(session=session, statement=statement)


class TestUpdateObject:
    def test_exists_object(self, session, admin_user):
        expected_object = copy(admin_user)
        expected_object.username = "some_another_username"
        object_in_db = base_services.update_object(
            session=session,
            model=User,
            where_statements=[User.username == admin_user.username],
            to_update={"username": "some_another_username"},
        )
        assert expected_object == object_in_db

    def test_not_exists_object(self, session):
        with pytest.raises(HTTPException) as exception_info:
            base_services.update_object(
                session=session,
                model=User,
                where_statements=[User.username == "some_username"],
                to_update={"username": "another_some_username"}
            )
            assert exception_info.value.status_code == 404


class TestInsertObject:
    def test_not_exists_object(self, session, admin_user_data):
        inserted_object = base_services.insert_object(
            session=session,
            model=User,
            to_insert=admin_user_data,
        )
        assert inserted_object

    def test_exists_object(self, session, admin_user, admin_user_data):
        with pytest.raises(HTTPException) as exception_info:
            base_services.insert_object(
                session=session,
                model=User,
                to_insert=admin_user_data,
            )
            assert exception_info.value.status_code == 409


class TestDeleteObject:
    def test_exists_object(self, session, admin_user):
        deleted_object = base_services.delete_object(
            session=session,
            model=User,
            where_statements=[User.username == admin_user.username],
        )
        assert admin_user == deleted_object
        assert not base_services.is_object_exists(session=session, statement=User.id == admin_user.id)

    def test_not_exists_object(self, session):
        with pytest.raises(HTTPException) as exception_info:
            base_services.delete_object(
                session=session,
                model=User,
                where_statements=[User.username == "some_username"],
            )
        assert exception_info.value.status_code == 404


class TestGetObjects:
    def test_for_exist_objects(self, session, admin_user):
        objects = base_services.get_objects(session=session, model=User)
        assert objects == [admin_user]

    def test_for_not_exists_objects(self, session):
        objects = base_services.get_objects(session=session, model=User)
        assert objects == []
