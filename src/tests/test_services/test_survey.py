import uuid
from typing import List

import pytest
from faker import Faker
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, SurveyAttribute, Survey
from app.schemas.survey import SurveyCreate, SurveyBase, SurveyUpdate, SurveyAttributeUpdate
from app.services import survey as survey_services

fake = Faker()


class TestCreateSurvey:
    @pytest.mark.parametrize("build_survey_attrs", [3], indirect=True)
    async def test_for_not_exists(
            self,
            admin_user: User,
            session: AsyncSession,
            build_surveys: Survey,
            build_survey_attrs: List[SurveyAttribute]
    ):
        attrs = list(attr.as_dict() for attr in build_survey_attrs)
        survey = SurveyCreate(**build_surveys.as_dict(), attrs=attrs)
        survey = await survey_services.create_survey(session=session, survey=survey, user_id=admin_user.id)
        assert SurveyBase(**build_surveys.as_dict()) == SurveyBase(**survey.as_dict())


class TestGetSurvey:
    @pytest.mark.parametrize("factory_surveys", [2], indirect=True)
    async def test_for_exists(self, session: AsyncSession, factory_surveys: List[Survey]):
        survey = await survey_services.get_survey(session=session, id_=factory_surveys[1].id)
        assert survey

    async def test_for_not_exists(self, session: AsyncSession):
        with pytest.raises(HTTPException) as exception_info:
            await survey_services.get_survey(session=session, id_=uuid.uuid4())
            assert exception_info.value.status_code == 404


class TestGetSurveys:
    @pytest.mark.parametrize("factory_surveys", [5], indirect=True)
    async def test_for_exists(self, session: AsyncSession, factory_surveys: List[Survey]):
        surveys = await survey_services.get_surveys(session=session)
        assert len(surveys) == 5

    async def test_for_not_exists(self, session: AsyncSession):
        surveys = await survey_services.get_surveys(session=session)
        assert not surveys

    @pytest.mark.parametrize("factory_surveys", [5], indirect=True)
    async def test_if_available_true(self, session: AsyncSession, factory_surveys: List[Survey]):
        surveys = await survey_services.get_surveys(session=session, available=True)
        assert all([survey.available for survey in surveys])

    @pytest.mark.parametrize("factory_surveys", [5], indirect=True)
    async def test_if_available_false(self, session: AsyncSession, factory_surveys: List[Survey]):
        surveys = await survey_services.get_surveys(session=session, available=False)
        assert not all([survey.available for survey in surveys])


class TestUpdateSurvey:
    async def test_for_exists(self, session: AsyncSession, admin_user: User, factory_surveys: Survey):
        name = fake.name()
        to_update = SurveyUpdate(name=name)
        survey = await survey_services.update_survey(
            session=session,
            user=admin_user,
            id_=factory_surveys.id,
            to_update=to_update
        )
        assert survey.name == name

    async def test_for_not_exists(self, session: AsyncSession, admin_user: User):
        to_update = SurveyUpdate(name="another name")
        with pytest.raises(HTTPException) as exception:
            await survey_services.update_survey(session=session, user=admin_user, id_=uuid.uuid4(), to_update=to_update)
            assert exception.value.status_code == 404


class TestUpdateSurveyAttribute:
    async def test_for_exists(self, session: AsyncSession, factory_surveys: Survey, admin_user: User):
        question = fake.text()
        to_update = SurveyAttributeUpdate(question=question)
        survey_attr = await survey_services.update_survey_attribute(
            session=session,
            id_=factory_surveys.attrs[0].id,
            user=admin_user,
            to_update=to_update,
        )
        assert survey_attr.question == question

    async def test_for_not_exists(self, session: AsyncSession, admin_user: User):
        to_update = SurveyAttributeUpdate(question="text")
        with pytest.raises(HTTPException) as exception_info:
            await survey_services.update_survey_attribute(
                session=session,
                user=admin_user,
                id_=uuid.uuid4(),
                to_update=to_update,
            )
            assert exception_info.value.status_code == 404
