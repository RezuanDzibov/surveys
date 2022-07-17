from uuid import uuid4

import pytest
from fastapi import HTTPException
from psycopg2.errors import ForeignKeyViolation
from sqlalchemy import select

import crud
from auth import services as auth_services
from db.models import Verification


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


class TestVerifyRegistrationUser:
    def test_for_exists_verification(self, db_session, admin_user):
        verification = auth_services.create_verification(
            session=db_session,
            user_id=str(admin_user.get("id")),
        )
        auth_services.verify_registration_user(
            session=db_session,
            verification_id=verification.get("id"),
        )
        statement = select(Verification).where(Verification.id == verification.get("id"))
        assert not crud.is_object_exists(
            session=db_session,
            statement=statement,
        )

    def test_for_not_exists_verification(self, db_session):
        with pytest.raises(HTTPException) as exception_info:
            auth_services.verify_registration_user(
                session=db_session,
                verification_id=str(uuid4())
            )
            assert exception_info.value.status_code == 404


class TestRecoverPassword:
    def test_for_exists_user(self, db_session, task, admin_user):
        reset_token = auth_services.recover_password(
            session=db_session,
            task=task,
            email=admin_user.get("email"),
        )
        assert auth_services.verify_password_reset_token(token=reset_token)

    def test_for_not_exists_user(self, db_session, task):
        with pytest.raises(HTTPException) as exception_info:
            auth_services.recover_password(
                session=db_session,
                task=task,
                email="some_email@gmail.com",
            )
            assert exception_info.value.status_code == 404
