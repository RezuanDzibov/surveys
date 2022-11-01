import asyncio
import json
from functools import partial
from random import randint
from typing import List, Dict, Union
from unittest import mock

import pytest
from _pytest.fixtures import SubRequest
from httpx import AsyncClient
from pytest_factoryboy import register
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.security import get_password_hash
from app.core.settings import get_settings
from app.initial_data import create_admin_user, get_admin_user_data
from app.main import app
from app.models import Base, User, Survey, SurveyAttribute, Answer
from app.schemas import survey as survey_schemas
from app.services.answer import create_answer_attrs
from app.services.base import is_object_exists
from app.services.survey import create_survey_attrs
from app.services.user import get_user
from tests.factories import UserFactory, SurveyAttributeFactory, SurveyFactory, AnswerAttributeFactory, AnswerFactory
from tests.utils import build_answer_attrs_with_survey_attrs

settings = get_settings()

register(UserFactory)
register(SurveyAttributeFactory)
register(SurveyFactory)
register(AnswerAttributeFactory)
register(AnswerFactory)


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
    with mock.patch("app.core.emails.send_email"):
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
    return sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False, class_=AsyncSession)


@pytest.fixture(scope="function")
async def session(tables, session_maker) -> AsyncSession:
    async with session_maker() as session:
        yield session


@pytest.fixture(scope="function")
async def admin_user(request, session: AsyncSession) -> User:
    if not await is_object_exists(session=session, where_statement=User.email == settings.ADMIN_FIXTURE_EMAIL):
        create_admin_user_ = partial(create_admin_user, session)
        if hasattr(request, "param"):
            return await create_admin_user_(data_to_replace=request.param)
        return await create_admin_user_()
    return await get_user(session=session, where_statements=[User.email == settings.ADMIN_FIXTURE_EMAIL])


@pytest.fixture(scope="function")
async def admin_user_data() -> dict:
    return get_admin_user_data()


@pytest.fixture(scope="function")
async def task() -> mock.Mock:
    task = mock.Mock()
    task.add_task = mock.MagicMock()
    return task


@pytest.fixture(scope="function")
async def factory_users(request, session: AsyncSession, user_factory: UserFactory) -> Union[User, List[User]]:
    users: List[User] = user_factory.build_batch(request.param)
    session.add_all(users)
    await session.commit()
    return users


@pytest.fixture(scope="function")
async def factory_user(session: AsyncSession, user_factory: UserFactory):
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
) -> List[Survey]:
    if hasattr(request, "param"):
        surveys = survey_factory.build_batch(request.param)
    else:
        surveys = survey_factory.build_batch(randint(1, 10))
    for survey in surveys:
        survey.user_id = admin_user.id
    session.add_all(surveys)
    await session.commit()
    for survey in surveys:
        survey.__dict__["attrs"] = await create_survey_attrs(
            session=session,
            survey_id=survey.id,
            attrs=[attr.as_dict() for attr in survey_attribute_factory.build_batch(randint(1, 10))]
        )
    return surveys


@pytest.fixture(scope="function")
async def factory_survey(
        session: AsyncSession,
        admin_user: User,
        survey_attribute_factory: SurveyAttributeFactory,
        survey_factory: SurveyFactory
) -> Survey:
    attrs = survey_attribute_factory.build_batch(randint(1, 10))
    attrs = list([attr.as_dict() for attr in attrs])
    survey = survey_factory.build()
    survey.user_id = admin_user.id
    session.add(survey)
    await session.commit()
    attrs = await create_survey_attrs(session=session, survey_id=survey.id, attrs=attrs)
    survey.__dict__["attrs"] = attrs
    return survey


@pytest.fixture(scope="function")
async def user_and_its_pass(request: SubRequest, session: AsyncSession) -> dict:
    password = "password"
    if hasattr(request, "param") and isinstance(request.param, dict):
        user = UserFactory(**request.param, password=get_password_hash(password))
    else:
        user = UserFactory(is_active=True, password=get_password_hash(password))
    session.add(user)
    await session.commit()
    return {"user": user, "password": password}


@pytest.fixture(scope="function")
async def access_token_and_user(session: AsyncSession, test_client: AsyncClient, user_and_its_pass: dict) -> dict:
    response = await test_client.post(
        "auth/login/access-token",
        data={
            "login": user_and_its_pass["user"].username,
            "password": user_and_its_pass["password"],
        }
    )
    response_content = json.loads(response.content.decode("utf-8"))
    access_token = response_content.get("access_token")
    return {"access_token": access_token, "user": user_and_its_pass["user"]}


@pytest.fixture(scope="function")
async def build_answer_attrs(
        request: SubRequest,
        session: AsyncSession,
        answer_attribute_factory: AnswerAttributeFactory
) -> List[SurveyAttribute]:
    if hasattr(request, "param") and isinstance(request.param, int):
        attrs = answer_attribute_factory.build_batch(request.param)
    else:
        attrs = answer_attribute_factory.build_batch(randint(1, 10))
    return attrs


@pytest.fixture(scope="function")
async def factory_answer(
        request: SubRequest,
        session: AsyncSession,
        admin_user: User,
        factory_survey: Survey
) -> Answer:
    answer = Answer()
    answer.user_id = admin_user.id
    answer.survey_id = factory_survey.id
    session.add(answer)
    await session.commit()
    if hasattr(request, "param") and request.param is True:
        attrs = await build_answer_attrs_with_survey_attrs(survey=factory_survey)
        attrs = list([survey_schemas.AnswerAttribute(**attr) for attr in attrs])
        attrs = await create_answer_attrs(session=session, attrs=attrs, answer_id=answer.id)
        answer.__dict__["attrs"] = attrs
    return answer


@pytest.fixture(scope="function")
async def factory_answers(
        request: SubRequest,
        session: AsyncSession,
        admin_user: User,
        factory_surveys: List[Survey],
        answer_factory: AnswerFactory
) -> List[Answer]:
    answers = list()
    for answer, survey in zip(answer_factory.build_batch(len(factory_surveys)), factory_surveys):
        answer.user_id = admin_user.id
        answer.survey_id = survey.id
        session.add(answer)
        await session.commit()
        if hasattr(request, "param") and request.param is True:
            attrs = await build_answer_attrs_with_survey_attrs(survey=survey)
            attrs = list([survey_schemas.AnswerAttribute(**attr) for attr in attrs])
            attrs = await create_answer_attrs(session=session, attrs=attrs, answer_id=answer.id)
            answer.__dict__["attrs"] = attrs
        answers.append(answer)
    return answers


@pytest.fixture(scope="function")
async def user_auth_test_client(access_token_and_user: dict) -> AsyncClient:
    async with AsyncClient(app=app, base_url="http://testserver", headers={
        "Authorization": f"Bearer {access_token_and_user['access_token']}"
    }) as client:
        yield client


@pytest.fixture(scope="function")
async def user_auth_test_client(access_token_and_user: dict) -> AsyncClient:
    async with AsyncClient(app=app, base_url="http://testserver", headers={
        "Authorization": f"Bearer {access_token_and_user['access_token']}"
    }) as client:
        yield client


@pytest.fixture(scope="function")
async def build_answer(factory_survey: Survey, answer_factory: AnswerFactory) -> Answer:
    attrs = await build_answer_attrs_with_survey_attrs(survey=factory_survey)
    answer = answer_factory.build()
    answer.__dict__["attrs"] = attrs
    return answer
