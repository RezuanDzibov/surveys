import pytest
from fastapi import HTTPException
from sqlalchemy import select

from app import crud
from app.db.models import User
from app.settings import get_settings

settings = get_settings()


class TestGetObject:
    def test_get_object(self, session, admin_user):
        statement = select(User).where(User.id == admin_user.get("id"))
        object_in_db = crud.get_object(session=session, statement=statement)
        assert admin_user == object_in_db

    def test_get_object_id_as_str(self, session, admin_user):
        statement = select(User).where(User.id == str(admin_user.get("id")))
        object_in_db = crud.get_object(session=session, statement=statement)
        assert admin_user == object_in_db

    def test_get_not_exists_object(self, session):
        with pytest.raises(HTTPException) as exception_info:
            statement = select(User).where(User.username == "someusername")
            crud.get_object(session=session, statement=statement)
            assert exception_info.value.status_code == 404


class TestIsObjectExists:
    def test_exists_object(self, session, admin_user):
        statement = select(User).where(User.username == admin_user.get("username"))
        assert crud.is_object_exists(session=session, statement=statement)

    def test_not_exists_object(self, session):
        statement = select(User).where(User.username == "some username")
        assert not crud.is_object_exists(session=session, statement=statement)


class TestUpdateObject:
    def test_exists_object(self, session, admin_user):
        expected_object = admin_user.copy()
        expected_object["username"] = "some_another_username"
        object_in_db = crud.update_object(
            session=session,
            model=User,
            where_statements=[User.username == admin_user.get("username")],
            to_update={"username": "some_another_username"},
        )
        assert expected_object == object_in_db

    def test_not_exists_object(self, session):
        with pytest.raises(HTTPException) as exception_info:
            crud.update_object(
                session=session,
                model=User,
                where_statements=[User.username == "some_username"],
                to_update={"username": "another_some_username"}
            )
            assert exception_info.value.status_code == 404


class TestInsertObject:
    def test_not_exists_object(self, session, admin_user_data):
        inserted_object = crud.insert_object(
            session=session,
            model=User,
            to_insert=admin_user_data,
        )
        assert inserted_object

    def test_exists_object(self, session, admin_user, admin_user_data):
        with pytest.raises(HTTPException) as exception_info:
            crud.insert_object(
                session=session,
                model=User,
                to_insert=admin_user_data,
            )
            assert exception_info.value.status_code == 409


class TestDeleteObject:
    def test_exists_object(self, session, admin_user):
        deleted_object = crud.delete_object(
            session=session,
            model=User,
            where_statements=[User.username == admin_user.get("username")],
        )
        assert admin_user == deleted_object
        assert not crud.is_object_exists(session=session, statement=User.id == admin_user.get("id"))

    def test_not_exists_object(self, session):
        with pytest.raises(HTTPException) as exception_info:
            crud.delete_object(
                session=session,
                model=User,
                where_statements=[User.username == "some_username"],
            )
        assert exception_info.value.status_code == 404


class TestGetObjects:
    def test_for_exist_objects(self, session, admin_user):
        objects = crud.get_objects(session=session, model=User)
        assert objects == [User(**admin_user)]

    def test_for_not_exists_objects(self, session):
        objects = crud.get_objects(session=session, model=User)
        assert objects == []
