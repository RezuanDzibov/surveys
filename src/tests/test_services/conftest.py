from typing import List, Union

import pytest
from pytest_asyncio.plugin import SubRequest
from pytest_factoryboy import register
from sqlalchemy.ext.asyncio import AsyncSession

from models import SurveyAttribute, Survey, User
from services.survey import _create_survey_attributes
from tests.factories import SurveyAttributeFactory, SurveyFactory

register(SurveyAttributeFactory)


@pytest.fixture(scope="function")
async def build_survey_attrs(
        request: SubRequest,
        session: AsyncSession,
        survey_attribute_factory: SurveyAttributeFactory
) -> Union[SurveyAttribute, List[SurveyAttribute]]:
    if hasattr(request, "param"):
        attrs = survey_attribute_factory.build_batch(request.param["quantity"])
        return attrs
    attr = survey_attribute_factory.build()
    return attr
