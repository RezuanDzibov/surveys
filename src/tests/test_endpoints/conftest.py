import json
from typing import Dict

import pytest
from httpx import AsyncClient
from pytest_factoryboy import register

from models import User
from schemas.survey import SurveyCreate
from tests.factories import SurveyFactory

register(SurveyFactory)


@pytest.fixture(scope="function")
async def access_token_and_admin_user(
        test_client: AsyncClient,
        admin_user: User,
        admin_user_data: dict
) -> Dict[str, User]:
    response = await test_client.post(
        "auth/login/access-token",
        data={
            "login": admin_user_data.get("username"),
            "password": admin_user_data.get("password"),
        }
    )
    response_content = json.loads(response.content.decode("utf-8"))
    access_token = response_content.get("access_token")
    return {"access_token": access_token, "admin_user": admin_user}


@pytest.fixture(scope="function")
async def survey_data(survey_factory) -> dict:
    survey = survey_factory.build()
    survey = SurveyCreate.from_orm(survey).dict()
    return survey
