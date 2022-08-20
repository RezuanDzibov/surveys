from sqlalchemy.ext.asyncio import AsyncSession

from models import User
from schemas.survey import SurveyCreate, SurveyBase
from services import survey as survey_services
from tests.factories import SurveyAttributeFactory


class TestCreateSurvey:
    async def test_for_not_exists(
            self,
            admin_user: User,
            session: AsyncSession,
    ):
        survey_data = {"name": "name"}
        attrs = SurveyAttributeFactory.build_batch(3)
        attrs = [attr.as_dict() for attr in attrs]
        survey = SurveyCreate(**survey_data, attrs=attrs)
        survey = await survey_services.create_survey(session=session, survey=survey, user_id=admin_user.id)
        assert SurveyBase(**survey_data) == SurveyBase(**survey.as_dict())
