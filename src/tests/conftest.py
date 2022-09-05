import asyncio
from functools import partial
from typing import List, Dict, Union
from unittest import mock

import pytest
from _pytest.fixtures import SubRequest
from httpx import AsyncClient
from pytest_factoryboy import register
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from core.settings import get_settings
from initial_data import create_admin_user, get_admin_user_data
from main import app
from models import Base, User, Survey, SurveyAttribute
from services.survey import _create_survey_attributes
from tests.factories import UserFactory, SurveyAttributeFactory, SurveyFactory

settings = get_settings()

register(UserFactory)
register(SurveyAttributeFactory)
register(SurveyFactory)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def patch_send_email() -> None:
    """
    Patch send_email function to not send emails during tests
    :return: None
    """
    with mock.patch("core.emails.send_email"):
        yield


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
    if hasattr(request, "param"):
        return await create_admin_user_(data_to_replace=request.param)
    return await create_admin_user_()


@pytest.fixture(scope="function")
async def admin_user_data() -> dict:
    return get_admin_user_data()


@pytest.fixture(scope="function")
async def task() -> mock.Mock:
    task = mock.Mock()
    task.add_task = mock.MagicMock()
    return task


@pytest.fixture(scope="function")
async def factory_users(request, session: AsyncSession, user_factory: UserFactory) -> List[User]:
    if request.param:
        users: List[User] = user_factory.build_batch(request.param)
        session.add_all(users)
        await session.commit()
        [await session.refresh(user) for user in users]
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


@pytest.fixture(scope="function")
async def build_survey_attrs(
        request: SubRequest,
        session: AsyncSession,
        survey_attribute_factory: SurveyAttributeFactory
) -> Union[SurveyAttribute, List[SurveyAttribute]]:
    if hasattr(request, "param"):
        attrs = survey_attribute_factory.build_batch(request.param)
        return attrs
    attr = survey_attribute_factory.build()
    return attr


@pytest.fixture(scope="function")
async def build_surveys(request: SubRequest, survey_factory: SurveyFactory) -> Union[Survey, List[Survey]]:
    if hasattr(request, "param"):
        surveys = survey_factory.build_batch(request.param)
        return surveys
    survey = survey_factory.build()
    return survey


@pytest.fixture(scope="function")
async def factory_surveys(
        request: SubRequest,
        session: AsyncSession,
        admin_user: User,
        survey_factory: SurveyFactory,
        survey_attribute_factory: SurveyAttributeFactory
) -> Union[Survey, List[Survey]]:
    attrs = survey_attribute_factory.build_batch(3)
    attrs = list([attr.as_dict() for attr in attrs])
    if hasattr(request, "param"):
        surveys = survey_factory.build_batch(request.param)
        for survey in surveys:
            survey.user_id = str(admin_user.id)
        session.add_all(surveys)
        await session.commit()
        for survey in surveys:
            await session.refresh(survey)
            await _create_survey_attributes(session=session, survey_id=str(survey.id), attrs=attrs)
        for survey in surveys:
            await session.refresh(survey)
        return surveys
    survey = survey_factory.build()
    survey.user_id = str(admin_user.id)
    session.add(survey)
    await session.commit()
    await session.refresh(survey)
    await _create_survey_attributes(session=session, survey_id=str(survey.id), attrs=attrs)
    await session.refresh(survey)
    return survey
