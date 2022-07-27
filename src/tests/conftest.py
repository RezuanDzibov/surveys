from functools import partial
from unittest import mock

import pytest
from fastapi.testclient import TestClient
from pytest_factoryboy import register
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session

from app.db.models import Base
from app.db.models import User
from app.initial_data_fixtures import create_admin_user
from app.main import app
from app.settings import get_settings
from tests.factories import UserFactory

settings = get_settings()

register(UserFactory)


@pytest.fixture(scope="session")
def engine() -> Engine:
    return create_engine(settings.SQLALCHEMY_DATABASE_URI)


@pytest.fixture(scope="function")
def tables(engine) -> None:
    Base.metadata.create_all(engine)
    try:
        yield
    finally:
        Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def session_maker(engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def session(tables, session_maker) -> Session:
    session = session_maker()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def admin_user(request, session) -> dict:
    create_admin_user_ = partial(create_admin_user, session)
    return create_admin_user_(data_to_replace=request.param) if hasattr(request, "param") else create_admin_user_()


@pytest.fixture(scope="function")
def admin_user_data() -> dict:
    return {
        "username": settings.ADMIN_FIXTURE_USERNAME,
        "email": settings.ADMIN_FIXTURE_EMAIL,
        "password": settings.ADMIN_FIXTURE_PASSWORD,
        "first_name": settings.ADMIN_FIXTURE_FIRST_NAME,
        "last_name": settings.ADMIN_FIXTURE_LAST_NAME,
        "birth_date": settings.ADMIN_FIXTURE_BIRTH_DATE,
        "is_active": settings.ADMIN_FIXTURE_IS_ACTIVE,
        "is_stuff": settings.ADMIN_FIXTURE_IS_STUFF,
        "is_superuser": settings.ADMIN_FIXTURE_IS_SUPERUSER,
    }


@pytest.fixture(scope="function")
def task() -> mock.Mock:
    task = mock.Mock()
    task.add_task = mock.MagicMock()
    return task


@pytest.fixture(scope="function")
def test_client() -> TestClient:
    return TestClient(app)


@pytest.fixture(scope="function")
def factory_users(request, session: Session, user_factory: UserFactory) -> list[User]:
    if request.param:
        users: [User] = user_factory.build_batch(request.param)
        session.add_all(users)
        session.commit()
        return users
    return user_factory.create()
