from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.db.models import User
from app.user import services
from app.user.schemas import UserRegistrationIn


class TestCreateUser:
    def test_create_user(self, session, admin_user_data, task):
        user_to_insert = UserRegistrationIn(**admin_user_data)
        user = services.create_user(
            session=session,
            new_user=user_to_insert,
            task=task,
        )
        assert user

    def test_create_user_with_exists_username(self, session, admin_user, admin_user_data, task):
        admin_user_data["email"] = "someanotheremail@gmail.com"
        user_to_insert = UserRegistrationIn(**admin_user_data)
        with pytest.raises(HTTPException) as exception_info:
            services.create_user(
                session=session,
                new_user=user_to_insert,
                task=task,
            )
        assert exception_info.value.status_code == 409

    def test_create_user_with_exists_email(self, session, admin_user, admin_user_data, task):
        admin_user_data["username"] = "someanotherusername"
        user_to_insert = UserRegistrationIn(**admin_user_data)
        with pytest.raises(HTTPException) as exception_info:
            services.create_user(
                session=session,
                new_user=user_to_insert,
                task=task,
            )
        assert exception_info.value.status_code == 409


class TestGetUser:
    def test_exists_user_search_by_id(self, session, admin_user):
        user = services.get_user(session=session, where_statements=[User.id == admin_user.get("id")])
        assert user == admin_user

    def test_exists_user_search_by_username(self, session, admin_user):
        user = services.get_user(session=session, where_statements=[User.username == admin_user.get("username")])
        assert user == admin_user

    def test_exists_user_search_by_email(self, session, admin_user):
        user = services.get_user(session=session, where_statements=[User.email == admin_user.get("email")])
        assert user == admin_user

    def test_not_exists_search_by_id(self, session):
        with pytest.raises(HTTPException) as exception_info:
            services.get_user(session=session, where_statements=[User.id == uuid4()])
            assert exception_info.value.status_code == 404

    def test_not_exists_search_by_username(self, session):
        with pytest.raises(HTTPException) as exception_info:
            services.get_user(session=session, where_statements=[User.username == "some username"])
            assert exception_info.value.status_code == 404

    def test_not_exists_search_by_email(self, session):
        with pytest.raises(HTTPException) as exception_info:
            services.get_user(session=session, where_statements=[User.email == "someemail@gmail.com"])
            assert exception_info.value.status_code == 404


class TestUpdateUser:
    def test_update_exists_user(self, session, admin_user):
        admin_user["username"] = "some_another_username"
        user_in_db = services.update_user(
            session=session,
            where_statements=[User.id == admin_user.get("id")],
            to_update={"username": "some_another_username"},
        )
        assert admin_user == user_in_db

    def test_update_not_exists_object(self, session):
        with pytest.raises(HTTPException) as exception_info:
            services.update_user(
                session=session,
                to_update={"username": "some"},
                where_statements=[User.username == "some0"],
            )
            assert exception_info.value.status_code == 404


class TestGetUsers:
    @pytest.mark.parametrize("factory_users", [5], indirect=True)
    def test_for_exists_users(self, session, factory_users):
        users = services.get_users(session=session)
        assert len(users) == 5

    def test_for_not_exists_users(self, session):
        users = services.get_users(session=session)
        assert len(users) == 0
