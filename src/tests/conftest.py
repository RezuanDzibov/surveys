from functools import partial
from unittest import mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models import Base
from app.initial_data_fixtures import create_admin_user
from app.main import app
from app.settings import get_settings

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
def session(tables, session_maker):
    session = session_maker()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def admin_user(request, session):
    create_admin_user_ = partial(create_admin_user, session)
    return create_admin_user_(data_to_replace=request.param) if hasattr(request, "param") else create_admin_user_()


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


@pytest.fixture(scope="function")
def test_client():
    return TestClient(app)
