import pytest
from fastapi import HTTPException
from sqlalchemy import select

import crud
from db.models import User
from initial_data_fixtures import create_admin_user
from settings import get_settings

settings = get_settings()


class TestGetObject:
    def test_get_object(self, db_session):
        expected_object = create_admin_user()
        statement = select(User).where(User.id == expected_object.get("id"))
        object_in_db = crud.get_object(session=db_session, statement=statement)
        assert expected_object == object_in_db

    def test_get_object_id_as_str(self, db_session):
        expected_object = create_admin_user()
        statement = select(User).where(User.id == str(expected_object.get("id")))
        object_in_db = crud.get_object(session=db_session, statement=statement)
        assert expected_object == object_in_db

    def test_get_not_exists_object(self, db_session):
        with pytest.raises(HTTPException) as exception_info:
            statement = select(User).where(User.username == "someusername")
            crud.get_object(session=db_session, statement=statement)
            assert exception_info.value.status_code == 404


class TestIsObjectExists:
    def test_exists_object(self, db_session):
        object_ = create_admin_user()
        statement = select(User).where(User.username == object_.get("username"))
        assert crud.is_object_exists(session=db_session, statement=statement)

    def test_not_exists_object(self, db_session):
        statement = select(User).where(User.username == "some username")
        assert not crud.is_object_exists(session=db_session, statement=statement)


class TestUpdateObject:
    def test_exists_object(self, db_session):
        object_ = create_admin_user()
        expected_object = object_.copy()
        expected_object["username"] = "some_another_username"
        object_in_db = crud.update_object(
            session=db_session,
            model=User,
            where_statements=[User.username == object_.get("username")],
            to_update={"username": "some_another_username"},
        )
        assert expected_object == object_in_db

    def test_not_exists_object(self, db_session):
        with pytest.raises(HTTPException) as exception_info:
            crud.update_object(
                session=db_session,
                model=User,
                where_statements=[User.username == "some_username"],
                to_update={"username": "another_some_username"}
            )
            assert exception_info.value.status_code == 404


class TestInsertObject:
    def test_not_exists_object(self, db_session, admin_user_data):
        inserted_object = crud.insert_object(
            session=db_session,
            model=User,
            to_insert=admin_user_data,
        )
        assert inserted_object

    def test_exists_object(self, db_session, admin_user, admin_user_data):
        with pytest.raises(HTTPException) as exception_info:
            crud.insert_object(
                session=db_session,
                model=User,
                to_insert=admin_user_data,
            )
            assert exception_info.value.status_code == 409


class TestDeleteObject:
    def test_exists_object(self, db_session, admin_user):
        deleted_object = crud.delete_object(
            session=db_session,
            model=User,
            where_statements=[User.username == admin_user.get("username")],
        )
        assert admin_user == deleted_object

    def test_not_exists_object(self, db_session):
        with pytest.raises(HTTPException) as exception_info:
            crud.delete_object(
                session=db_session,
                model=User,
                where_statements=[User.username == "some_username"],
            )
        assert exception_info.value.status_code == 404
