from unittest import mock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.models import Base
from initial_data_fixtures import create_admin_user
from settings import get_settings

settings = get_settings()


@pytest.fixture(scope="session")
def engine():
    return create_engine(settings.SQLALCHEMY_DATABASE_URI)


@pytest.fixture(scope="function")
def tables(engine):
    Base.metadata.create_all(engine)
    try:
        yield
    finally:
        Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def session_maker(engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session(tables, session_maker):
    session = session_maker()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def admin_user(db_session):
    return create_admin_user()


@pytest.fixture(scope="function")
def admin_user_data():
    return {
        "username": settings.ADMIN_FIXTURE_USERNAME,
        "email": settings.ADMIN_FIXTURE_EMAIL,
        "password": settings.ADMIN_FIXTURE_PASSWORD,
        "first_name": settings.ADMIN_FIXTURE_FIRST_NAME,
        "last_name": settings.ADMIN_FIXTURE_LAST_NAME,
        "birth_date": settings.ADMIN_FIXTURE_BIRTH_DATE,
        "is_active": settings.ADMIN_FIXTURE_IS_ACTIVE,
        "is_staff": settings.ADMIN_FIXTURE_IS_STUFF,
        "is_superuser": settings.ADMIN_FIXTURE_IS_SUPERUSER,
    }


@pytest.fixture(scope="function")
def task():
    task = mock.Mock()
    task.add_task = mock.MagicMock()
    return task
