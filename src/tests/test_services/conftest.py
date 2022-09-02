from typing import List, Union

import pytest
from pytest_asyncio.plugin import SubRequest
from pytest_factoryboy import register
from sqlalchemy.ext.asyncio import AsyncSession

from models import SurveyAttribute, Survey, User
from services.survey import _create_survey_attributes
from tests.factories import SurveyAttributeFactory, SurveyFactory

register(SurveyAttributeFactory)
register(SurveyFactory)


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
