import uuid
from typing import List

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from models import User, SurveyAttribute
from schemas.survey import SurveyCreate, SurveyBase, Survey
from services import survey as survey_services


class TestCreateSurvey:
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
