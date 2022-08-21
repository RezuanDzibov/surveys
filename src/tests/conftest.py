import asyncio
from functools import partial
from typing import List, Dict
from unittest import mock

import pytest
from httpx import AsyncClient
from pytest_factoryboy import register
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from core.settings import get_settings
from initial_data import create_admin_user, get_admin_user_data
from main import app
from models import Base, User
from tests.factories import UserFactory

settings = get_settings()

register(UserFactory)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def engine() -> Engine:
    return create_async_engine(settings.SQLALCHEMY_DATABASE_URI)


@pytest.fixture(scope="function")
async def tables(engine) -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
    await engine.dispose()


@pytest.fixture(scope="function")
async def session_maker(engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)


@pytest.fixture(scope="function")
async def session(tables, session_maker) -> AsyncSession:
    async with session_maker() as session:
        yield session


@pytest.fixture(scope="function")
async def admin_user(request, session: AsyncSession) -> User:
    create_admin_user_ = partial(create_admin_user, session)
    return await create_admin_user_(data_to_replace=request.param) if hasattr(request, "param") else await create_admin_user_()


@pytest.fixture(scope="function")
def admin_user_data() -> dict:
    return get_admin_user_data()


@pytest.fixture(scope="function")
def task() -> mock.Mock:
    task = mock.Mock()
    task.add_task = mock.MagicMock()
    return task


@pytest.fixture(scope="function")
async def factory_users(request, session: AsyncSession, user_factory: UserFactory) -> List[User]:
    if request.param:
        users: [User] = user_factory.build_batch(request.param)
        session.add_all(users)
        await session.commit()
        return users
    user = user_factory.build()
    session.add(user)
    await session.commit()
    return user


@pytest.fixture(scope="function")
async def test_client() -> AsyncClient:
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


@pytest.fixture(scope="function")
async def auth_test_client(access_token_and_admin_user: Dict[str, User]) -> AsyncClient:
    async with AsyncClient(app=app, base_url="http://testserver", headers={
        "Authorization": f"Bearer {access_token_and_admin_user['access_token']}"
    }) as client:
        yield client
