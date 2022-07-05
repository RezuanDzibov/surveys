from unittest import mock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from user import services
from user.schemas import UserRegistrationIn
from db.models import User


class TestCreateUser:
    def test_create_user(self, db_session, admin_user_data):
        user_to_insert = UserRegistrationIn(**admin_user_data)
        task = mock.MagicMock()
        task.add_task = mock.Mock(return_value=None)
        user = services.create_user(
            session=db_session,
            new_user=user_to_insert,
            task=task,
        )
        assert user

    def test_create_user_with_exists_username(self, db_session, admin_user, admin_user_data):
        admin_user_data["email"] = "someanotheremail@gmail.com"
        user_to_insert = UserRegistrationIn(**admin_user_data)
        task = mock.MagicMock()
        task.add_task = mock.Mock(return_value=None)
        with pytest.raises(HTTPException) as exception_info:
            services.create_user(
                session=db_session,
                new_user=user_to_insert,
                task=task,
            )
        assert exception_info.value.status_code == 409

    def test_create_user_with_exists_email(self, db_session, admin_user, admin_user_data):
        admin_user_data["username"] = "someanotherusername"
        user_to_insert = UserRegistrationIn(**admin_user_data)
        task = mock.MagicMock()
        task.add_task = mock.Mock(return_value=None)
        with pytest.raises(HTTPException) as exception_info:
            services.create_user(
                session=db_session,
                new_user=user_to_insert,
                task=task,
            )
        assert exception_info.value.status_code == 409


class TestGetUser:
    def test_exists_user_search_by_id(self, db_session, admin_user):
        user = services.get_user(session=db_session, where_statements=[User.id == admin_user.get("id")])
        assert user == admin_user

    def test_exists_user_search_by_username(self, db_session, admin_user):
        user = services.get_user(session=db_session, where_statements=[User.username == admin_user.get("username")])
        assert user == admin_user

    def test_exists_user_search_by_email(self, db_session, admin_user):
        user = services.get_user(session=db_session, where_statements=[User.email == admin_user.get("email")])
        assert user == admin_user

    def test_not_exists_search_by_id(self, db_session):
        with pytest.raises(HTTPException) as exception_info:
            services.get_user(session=db_session, where_statements=[User.id == uuid4()])
            assert exception_info.value.status_code == 404

    def test_not_exists_search_by_username(self, db_session):
        with pytest.raises(HTTPException) as exception_info:
            services.get_user(session=db_session, where_statements=[User.username == "some username"])
            assert exception_info.value.status_code == 404

    def test_not_exists_search_by_email(self, db_session):
        with pytest.raises(HTTPException) as exception_info:
            services.get_user(session=db_session, where_statements=[User.id == "someemail@gmail.com"])
            assert exception_info.value.status_code == 404
