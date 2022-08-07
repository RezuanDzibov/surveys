from functools import partial
from unittest import mock

import pytest
from fastapi.testclient import TestClient
from pytest_factoryboy import register
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session

from core.settings import get_settings
from initial_data import create_admin_user, get_admin_user_data
from main import app
from models import Base, User
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
def admin_user(request, session) -> User:
    create_admin_user_ = partial(create_admin_user, session)
    return create_admin_user_(data_to_replace=request.param) if hasattr(request, "param") else create_admin_user_()


@pytest.fixture(scope="function")
def admin_user_data() -> dict:
    return get_admin_user_data()


@pytest.fixture(scope="function")
def task() -> mock.Mock:
    task = mock.Mock()
    task.add_task = mock.MagicMock()
    return task


@pytest.fixture(scope="function")
def factory_users(request, session: Session, user_factory: UserFactory) -> list[User]:
    if request.param:
        users: [User] = user_factory.build_batch(request.param)
        session.add_all(users)
        session.commit()
        return users
    return user_factory.create()


@pytest.fixture(scope="function")
def test_client() -> TestClient:
    return TestClient(app, base_url="https://testserver/")
