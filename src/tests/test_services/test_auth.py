from uuid import uuid4

import pytest
from fastapi import HTTPException
from psycopg2.errors import ForeignKeyViolation
from sqlalchemy import select

from core.security import verify_password
from models import Verification, User
from services import auth as auth_services
from services import base as base_services


class TestAuthenticate:
    def test_for_exists_user_by_username(self, session, admin_user, admin_user_data):
        user_in_db = auth_services.authenticate(
            session=session,
            login=admin_user.username,
            password=admin_user_data.get("password"),
        )
        assert admin_user == user_in_db

    def test_for_exists_user_by_email(self, session, admin_user, admin_user_data):
        user_in_db = auth_services.authenticate(
            session=session,
            login=admin_user.email,
            password=admin_user_data.get("password"),
        )
        assert admin_user == user_in_db

    def test_for_not_exists_user_by_username(self, session):
        with pytest.raises(HTTPException) as exception_info:
            auth_services.authenticate(
                session=session,
                login="some_username",
                password="some_pass",
            )
            assert exception_info.value.status_code == 404

    def test_for_not_exists_user_by_email(self, session):
        with pytest.raises(HTTPException) as exception_info:
            auth_services.authenticate(
                session=session,
                login="someemail@gmail.com",
                password="some_pass",
            )
            assert exception_info.value.status_code == 404

    def test_for_invalid_password_by_username(self, session, admin_user):
        with pytest.raises(HTTPException) as exception_info:
            auth_services.authenticate(
                session=session,
                login=admin_user.username,
                password="some_invalid_pass"
            )
            assert exception_info.value.status_code == 400

    def test_for_invalid_password_by_email(self, session, admin_user):
        with pytest.raises(HTTPException) as exception_info:
            auth_services.authenticate(
                session=session,
                login=admin_user.email,
                password="some_invalid_pass"
            )
            assert exception_info.value.status_code == 400


class TestCreateVerification:
    def test_for_exists_user(self, session, admin_user):
        verification = auth_services.create_verification(
            session=session,
            user_id=str(admin_user.id)
        )
        assert verification

    def test_for_not_exists_user(self, session):
        with pytest.raises(ForeignKeyViolation):
            auth_services.create_verification(
                session=session,
                user_id=str(uuid4())
            )


class TestVerifyRegistrationUser:
    def test_for_exists_verification(self, session, admin_user):
        verification = auth_services.create_verification(
            session=session,
            user_id=str(admin_user.id),
        )
        auth_services.verify_registration_user(
            session=session,
            verification_id=verification.id,
        )
        statement = select(Verification).where(Verification.id == verification.id)
        assert not base_services.is_object_exists(
            session=session,
            statement=statement,
        )

    def test_for_not_exists_verification(self, session):
        with pytest.raises(HTTPException) as exception_info:
            auth_services.verify_registration_user(
                session=session,
                verification_id=str(uuid4())
            )
            assert exception_info.value.status_code == 404


class TestVerifyPasswordResetToken:
    def test_for_valid_reset_token(self, session, admin_user, task):
        reset_token = auth_services.recover_password(
            session=session,
            task=task,
            email=admin_user.email,
        )
        email = auth_services.verify_password_reset_token(token=reset_token)
        assert email == admin_user.email

    def test_for_invalid_reset_token(self, session):
        email = auth_services.verify_password_reset_token(token="some_token")
        assert not email


class TestRecoverPassword:
    def test_for_exists_user(self, session, task, admin_user):
        reset_token = auth_services.recover_password(
            session=session,
            task=task,
            email=admin_user.email,
        )
        assert auth_services.verify_password_reset_token(token=reset_token)

    def test_for_not_exists_user(self, session, task):
        with pytest.raises(HTTPException) as exception_info:
            auth_services.recover_password(
                session=session,
                task=task,
                email="some_email@gmail.com",
            )
            assert exception_info.value.status_code == 404


class TestResetPassword:
    def test_for_valid_reset_token(self, session, task, admin_user):
        reset_token = auth_services.recover_password(
            session=session,
            task=task,
            email=admin_user.email,
        )
        updated_user = auth_services.reset_password(
            session=session,
            token=reset_token,
            new_password="some_new_pass"
        )
        assert verify_password("some_new_pass", updated_user.password)

    def test_for_invalid_reset_token(self, session):
        with pytest.raises(HTTPException) as exception_info:
            auth_services.reset_password(
                session=session,
                token="some_token",
                new_password="some_new_pass"
            )
        assert exception_info.value.status_code == 400

    def test_for_inactive_user(self, session, task, admin_user_data):
        admin_user_data["is_active"] = False
        base_services.insert_object(
            session=session,
            model=User,
            to_insert=admin_user_data,
            return_object=False
        )
        reset_token = auth_services.recover_password(
            session=session,
            task=task,
            email=admin_user_data.get("email"),
        )
        with pytest.raises(HTTPException) as exception_info:
            auth_services.reset_password(
                session=session,
                token=reset_token,
                new_password="some_new_pass"
            )
            assert exception_info.value.status_code == 400
