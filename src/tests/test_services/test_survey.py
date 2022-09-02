import uuid
from typing import List

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from models import User, SurveyAttribute
from schemas.survey import SurveyCreate, SurveyBase, Survey
from services import survey as survey_services


class TestCreateSurvey:
    @pytest.mark.parametrize("build_survey_attrs", [3], indirect=True)
    async def test_for_not_exists(
            self,
            admin_user: User,
            session: AsyncSession,
            build_survey_attrs: List[SurveyAttribute]
    ):
        survey_data = {"name": "name"}
        attrs = list(attr.as_dict() for attr in build_survey_attrs)
        survey = SurveyCreate(**survey_data, attrs=attrs)
        survey = await survey_services.create_survey(session=session, survey=survey, user_id=admin_user.id)
        assert SurveyBase(**survey_data) == SurveyBase(**survey.as_dict())


class TestGetSurvey:
    @pytest.mark.parametrize("factory_surveys", [2], indirect=True)
    async def test_for_exists(self, session: AsyncSession, factory_surveys: List[Survey]):
        survey = await survey_services.get_survey(session=session, id_=str(factory_surveys[1].id))
        assert survey

    async def test_for_not_exists(self, session: AsyncSession):
        with pytest.raises(HTTPException) as exception_info:
            await survey_services.get_survey(session=session, id_=str(uuid.uuid4()))
            assert exception_info.value.status_code == 404
