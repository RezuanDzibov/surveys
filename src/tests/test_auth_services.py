from uuid import uuid4

import pytest
from fastapi import HTTPException
from psycopg2.errors import ForeignKeyViolation

from app.auth import services as auth_services


class TestAuthenticate:
    def test_for_exists_user_by_username(self, db_session, admin_user, admin_user_data):
        user_in_db = auth_services.authenticate(
            session=db_session,
            login=admin_user.get("username"),
            password=admin_user_data.get("password"),
        )
        assert admin_user == user_in_db

    def test_for_exists_user_by_email(self, db_session, admin_user, admin_user_data):
        user_in_db = auth_services.authenticate(
            session=db_session,
            login=admin_user.get("email"),
            password=admin_user_data.get("password"),
        )
        assert admin_user == user_in_db

    def test_for_not_exists_user_by_username(self, db_session):
        with pytest.raises(HTTPException) as exception_info:
            auth_services.authenticate(
                session=db_session,
                login="some_username",
                password="some_pass",
            )
            assert exception_info.value.status_code == 404

    def test_for_not_exists_user_by_email(self, db_session):
        with pytest.raises(HTTPException) as exception_info:
            auth_services.authenticate(
                session=db_session,
                login="someemail@gmail.com",
                password="some_pass",
            )
            assert exception_info.value.status_code == 404

    def test_for_invalid_password_by_username(self, db_session, admin_user):
        with pytest.raises(HTTPException) as exception_info:
            auth_services.authenticate(
                session=db_session,
                login=admin_user.get("username"),
                password="some_invalid_pass"
            )
            assert exception_info.value.status_code == 400

    def test_for_invalid_password_by_email(self, db_session, admin_user):
        with pytest.raises(HTTPException) as exception_info:
            auth_services.authenticate(
                session=db_session,
                login=admin_user.get("email"),
                password="some_invalid_pass"
            )
            assert exception_info.value.status_code == 400


class TestCreateVerification:
    def test_for_exists_user(self, db_session, admin_user):
        verification = auth_services.create_verification(
            session=db_session,
            user_id=str(admin_user.get("id"))
        )
        assert verification

    def test_for_not_exists_user(self, db_session):
        with pytest.raises(ForeignKeyViolation):
            auth_services.create_verification(
                session=db_session,
                user_id=str(uuid4())
            )
