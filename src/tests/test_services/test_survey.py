import random
import uuid
from typing import List

import pytest
from faker import Faker
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, SurveyAttribute, Survey
from app.schemas.survey import SurveyCreate, SurveyUpdate, SurveyAttributeUpdate, SurveyFilter
from app.services import base as base_services
from app.services import survey as survey_services
from app.services.filtering.survey import filter_surveys

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
        created_survey = await survey_services.create_survey(session=session, survey=survey, user_id=admin_user.id)
        assert survey == SurveyCreate(**created_survey.as_dict())


class TestGetSurvey:
    @pytest.mark.parametrize("factory_surveys", [2], indirect=True)
    async def test_for_exists(self, session: AsyncSession, admin_user: User, factory_surveys: List[Survey]):
        survey = await survey_services.get_survey(session=session, user=admin_user, id_=factory_surveys[1].id)
        assert factory_surveys[1] == survey

    async def test_for_not_exists(self, session: AsyncSession, admin_user: User):
        with pytest.raises(HTTPException) as exception_info:
            await survey_services.get_survey(session=session, user=admin_user, id_=uuid.uuid4())
            assert exception_info.value.status_code == 404

    @pytest.mark.parametrize("factory_surveys", [3], indirect=True)
    async def test_for_not_survey_author(
            self,
            session: AsyncSession,
            factory_surveys: List[Survey],
            factory_user: User
    ):
        survey = await survey_services.get_survey(session=session, user=factory_user, id_=factory_surveys[1].id)
        assert all([attr.available for attr in survey.attrs])
        
    @pytest.mark.parametrize("factory_surveys", [3], indirect=True)
    async def test_without_user(
            self,
            session: AsyncSession,
            factory_surveys: List[Survey],
    ):
        survey = await survey_services.get_survey(session=session, id_=factory_surveys[1].id)
        assert all([attr.available for attr in survey.attrs])


class TestGetSurveys:
    @pytest.mark.parametrize("factory_surveys", [5], indirect=True)
    async def test_for_exists(self, session: AsyncSession, factory_surveys: List[Survey]):
        surveys = await survey_services.get_surveys(session=session)
        assert all(survey.available is True for survey in surveys)

    async def test_for_not_exists(self, session: AsyncSession):
        surveys = await survey_services.get_surveys(session=session)
        assert not surveys


class TestUpdateSurvey:
    async def test_for_exists(self, session: AsyncSession, admin_user: User, factory_survey: Survey):
        name = fake.name()
        to_update = SurveyUpdate(name=name)
        survey = await survey_services.update_survey(
            session=session,
            user=admin_user,
            id_=factory_survey.id,
            to_update=to_update
        )
        assert survey.name == name

    async def test_for_not_exists(self, session: AsyncSession, admin_user: User):
        to_update = SurveyUpdate(name="another name")
        with pytest.raises(HTTPException) as exception:
            await survey_services.update_survey(session=session, user=admin_user, id_=uuid.uuid4(), to_update=to_update)
            assert exception.value.status_code == 404


class TestUpdateSurveyAttribute:
    async def test_for_exists(self, session: AsyncSession, factory_survey: Survey, admin_user: User):
        question = fake.text()
        to_update = SurveyAttributeUpdate(question=question)
        survey_attr = await survey_services.update_survey_attribute(
            session=session,
            id_=factory_survey.attrs[0].id,
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


class TestGetCurrentUserSurveys:
    @pytest.mark.parametrize("factory_surveys", [5], indirect=True)
    async def test_for_exists(self, session: AsyncSession, admin_user: User, factory_surveys: List[Survey]):
        surveys = await survey_services.get_current_user_surveys(session=session, user=admin_user)
        assert all(survey.user_id == admin_user.id for survey in surveys)

    async def test_for_not_exists(self, session: AsyncSession, admin_user: User):
        surveys = await survey_services.get_current_user_surveys(session=session, user=admin_user)
        assert not surveys

    async def test_if_available_is_true(self, session: AsyncSession, admin_user: User):
        surveys = await survey_services.get_current_user_surveys(session=session, user=admin_user, available=True)
        assert all(survey.available is True for survey in surveys)

    async def test_if_available_is_false(self, session: AsyncSession, admin_user: User):
        surveys = await survey_services.get_current_user_surveys(session=session, user=admin_user, available=False)
        assert all(survey.available is False for survey in surveys)


class TestGetUserSurveys:
    @pytest.mark.parametrize("factory_surveys", [5], indirect=True)
    async def test_for_exists(self, session: AsyncSession, admin_user: User, factory_surveys: List[Survey]):
        surveys = await survey_services.get_user_surveys(session=session, user_id=admin_user.id)
        assert all(survey.user_id == admin_user.id for survey in surveys)

    async def test_for_exists_user(self, session: AsyncSession):
        with pytest.raises(HTTPException) as exception_info:
            await survey_services.get_user_surveys(session=session, user_id=uuid.uuid4())
            assert exception_info.value.status_code == 404

    async def test_for_not_exists_survey(self, session: AsyncSession, admin_user: User):
        surveys = await survey_services.get_user_surveys(session=session, user_id=admin_user.id)
        assert not surveys


class TestGetSurveysWithFiltering:
    @pytest.mark.parametrize("factory_surveys", [5], indirect=True)
    async def test_searching_by_name(self, session: AsyncSession, factory_surveys: List[Survey]):
        surveys = await filter_surveys(session=session, filter=SurveyFilter(name=factory_surveys[0].name[:5]))
        assert all([survey.name.startswith(factory_surveys[0].name[:5]) for survey in surveys])

    @pytest.mark.parametrize("factory_surveys", [5], indirect=True)
    async def test_searching_by_email(self, session: AsyncSession, factory_surveys: List[Survey]):
        surveys = await filter_surveys(session=session, filter=SurveyFilter(description=factory_surveys[0].description[:30]))
        assert all([survey.description.startswith(factory_surveys[0].description[:30]) for survey in surveys])

    @pytest.mark.parametrize("factory_surveys", [5], indirect=True)
    async def test_searching_by_name_and_description(self, session: AsyncSession, factory_surveys: List[Survey]):
        surveys = await filter_surveys(
            session=session,
            filter=SurveyFilter(
                name=factory_surveys[0].name[:5],
                description=factory_surveys[0].description[:30]
            )
        )
        assert all([survey.name.startswith(factory_surveys[0].name[:5]) for survey in surveys])
        assert all([survey.description.startswith(factory_surveys[0].description[:30]) for survey in surveys])

    @pytest.mark.parametrize("factory_surveys", [5], indirect=True)
    async def test_for_not_exists(self, session: AsyncSession, factory_surveys: List[Survey]):
        surveys = await filter_surveys(session=session, filter=SurveyFilter(name="name"))
        assert not surveys


class TestDeleteSurvey:
    @pytest.mark.parametrize("factory_surveys", [5], indirect=True)
    async def test_success(self, session: AsyncSession, admin_user: User, factory_surveys: List[Survey]):
        deleted_survey = await survey_services.delete_survey(
            session=session,
            user=admin_user,
            id_=factory_surveys[2].id
        )
        assert deleted_survey == factory_surveys[2]
        assert not await base_services.is_object_exists(
            session=session,
            where_statement=select(Survey).where(Survey.id == factory_surveys[2].id)
        )

    @pytest.mark.parametrize("factory_surveys", [5], indirect=True)
    async def test_cascade_deletion(self, session: AsyncSession, admin_user: User, factory_surveys: List[Survey]):
        await survey_services.delete_survey(session=session, user=admin_user, id_=factory_surveys[2].id)
        assert not await base_services.is_object_exists(
            session=session,
            where_statement=select(SurveyAttribute).where(SurveyAttribute.id == factory_surveys[2].attrs[0].id)
        )

    async def test_404(self, session: AsyncSession, admin_user: User):
        with pytest.raises(HTTPException) as exception:
            await survey_services.delete_survey(session=session, user=admin_user, id_=uuid.uuid4())
            assert exception.value.status_code == 404

    @pytest.mark.parametrize("factory_surveys", [5], indirect=True)
    async def test_not_author(self, session: AsyncSession, factory_surveys: List[Survey], user_and_its_pass: dict,):
        with pytest.raises(HTTPException) as exception:
            await survey_services.delete_survey(
                session=session,
                user=user_and_its_pass["user"],
                id_=factory_surveys[2].id
                )
            assert exception.value.status_code == 404


class TestDeleteSurveyAttribute:
    @pytest.mark.parametrize("factory_surveys", [5], indirect=True)
    async def test_success(self, session: AsyncSession, admin_user: User, factory_surveys: List[Survey]):
        await survey_services.delete_survey_attribute(
            session=session,
            user=admin_user,
            id_=factory_surveys[2].attrs[0].id
        )
        assert not await base_services.is_object_exists(
            session=session,
            where_statement=select(SurveyAttribute).where(SurveyAttribute.id == factory_surveys[2].attrs[0].id)
        )

    async def test_404(self, session: AsyncSession, admin_user: User):
        with pytest.raises(HTTPException) as exception:
            await survey_services.delete_survey_attribute(session=session, user=admin_user, id_=uuid.uuid4())
            assert exception.value.status_code == 404

    @pytest.mark.parametrize("factory_surveys", [5], indirect=True)
    async def test_not_author(self, session: AsyncSession, factory_surveys: List[Survey], user_and_its_pass: dict,):
        with pytest.raises(HTTPException) as exception:
            await survey_services.delete_survey_attribute(
                session=session,
                user=user_and_its_pass["user"],
                id_=random.choice(random.choice(factory_surveys).attrs).id
                )
            assert exception.value.status_code == 404


class TestGetSurveyAttribute:
    @pytest.mark.parametrize("factory_surveys", [5], indirect=True)
    async def test_success(self, session: AsyncSession, admin_user: User, factory_surveys: List[Survey]):
        expected_attr = random.choice(random.choice(factory_surveys).attrs)
        attr_in_db = await survey_services.get_survey_attribute(
            session=session,
            user=admin_user,
            id_=expected_attr.id
        )
        assert expected_attr == attr_in_db

    async def test_404(self, session: AsyncSession, admin_user: User):
        with pytest.raises(HTTPException) as exception:
            await survey_services.get_survey_attribute(session=session, user=admin_user, id_=uuid.uuid4())
            assert exception.value.status_code == 404

    @pytest.mark.parametrize("factory_surveys", [5], indirect=True)
    async def test_author_success(self, session: AsyncSession, admin_user: User, factory_surveys: List[Survey]):
        expected_attr = None
        while not expected_attr:
            try:
                expected_attr = random.choice(
                    list(
                        filter(lambda attr: attr.available is False, random.choice(factory_surveys).attrs)
                    )
                )
            except IndexError:
                continue
        attr_in_db = await survey_services.get_survey_attribute(
            session=session,
            user=admin_user,
            id_=expected_attr.id
        )
        assert expected_attr == attr_in_db

    @pytest.mark.parametrize("factory_surveys", [5], indirect=True)
    async def test_not_author(self, session: AsyncSession, factory_surveys: List[Survey], user_and_its_pass: dict):
        expected_attr = None
        while not expected_attr:
            try:
                expected_attr = random.choice(
                    list(
                        filter(lambda attr: attr.available is False, random.choice(factory_surveys).attrs)
                    )
                )
            except IndexError:
                continue
        with pytest.raises(HTTPException) as exception:
            await survey_services.get_survey_attribute(
                session=session,
                user=user_and_its_pass["user"],
                id_=expected_attr.id
                )
            assert exception.value.status_code == 404

    @pytest.mark.parametrize("factory_surveys", [5], indirect=True)
    async def test_not_auth_user_available_is_true(
            self,
            session: AsyncSession,
            factory_surveys: List[Survey]
    ):
        expected_attr = None
        while not expected_attr:
            try:
                expected_attr = random.choice(
                    list(
                        filter(lambda attr: attr.available is True, random.choice(factory_surveys).attrs)
                    )
                )
            except IndexError:
                continue
        attr_in_db = await survey_services.get_survey_attribute(
            session=session,
            id_=expected_attr.id
        )
        assert expected_attr == attr_in_db

    @pytest.mark.parametrize("factory_surveys", [5], indirect=True)
    async def test_not_auth_user_available_is_false(
            self,
            session: AsyncSession,
            factory_surveys: List[Survey]
    ):
        expected_attr = None
        while not expected_attr:
            try:
                expected_attr = random.choice(
                    list(
                        filter(lambda attr: attr.available is False , random.choice(factory_surveys).attrs)
                    )
                )
            except IndexError:
                continue
        with pytest.raises(HTTPException) as exception:
            await survey_services.get_survey_attribute(
                session=session,
                id_=expected_attr.id
            )
            assert exception.value.status_code == 404
