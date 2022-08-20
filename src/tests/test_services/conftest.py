from typing import List

import pytest
from pytest_factoryboy import register
from sqlalchemy.ext.asyncio import AsyncSession

from models import SurveyAttribute
from tests.factories import SurveyAttributeFactory

register(SurveyAttributeFactory)


@pytest.fixture(scope="function")
async def factory_survey_attrs(
        request,
        session: AsyncSession,
        survey_attribute_factory: SurveyAttributeFactory
) -> List[SurveyAttribute]:
    if request.param:
        attrs: List[SurveyAttribute] = survey_attribute_factory.build_batch(request.param["quantity"])
        session.add_all(attrs)
        await session.commit()
        return attrs
    attr = survey_attribute_factory.build()
    session.add(attr)
    await session.commit()
    return attr
