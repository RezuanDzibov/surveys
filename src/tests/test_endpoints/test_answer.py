import json
from uuid import uuid4

from httpx import AsyncClient

from app.core.settings import get_settings
from app.models import Survey, Answer
from app.schemas import survey as schemas
from tests.factories import AnswerAttributeFactory
from tests.test_endpoints.utils import uuid_to_str, serialize_uuid_to_str
from tests.utils import build_answer_attrs_with_survey_attrs

settings = get_settings()


class TestAddAnswer:
    async def test_success(
            self,
            auth_test_client: AsyncClient,
            factory_survey: Survey

    ):
        attrs = await build_answer_attrs_with_survey_attrs(survey=factory_survey)
        expected_answer = await serialize_uuid_to_str(schemas.BaseAnswer(attrs=attrs).dict())
        response = await auth_test_client.post(f"/answer/{factory_survey.id}", json=expected_answer)
        created_answer = json.loads(response.content.decode("utf-8"))
        assert expected_answer == json.loads(json.dumps(schemas.BaseAnswer(**created_answer).dict(), default=uuid_to_str))

    async def test_not_exist_survey_attr(
            self,
            auth_test_client: AsyncClient,
            factory_survey: Survey

    ):
        attrs = await build_answer_attrs_with_survey_attrs(survey=factory_survey)
        attr = AnswerAttributeFactory.build()
        attr.survey_attr_id = str(uuid4())
        attrs.append(attr.as_dict())
        answer = await serialize_uuid_to_str(schemas.BaseAnswer(attrs=attrs).dict())
        response = await auth_test_client.post(f"/answer/{factory_survey.id}", json=answer)
        assert response.status_code == 404

    async def test_user_already_created_answer_for_survey(
            self,
            auth_test_client: AsyncClient,
            factory_survey: Survey,
            factory_answer: Answer
    ):
        attrs = await build_answer_attrs_with_survey_attrs(survey=factory_survey)
        answer = await serialize_uuid_to_str(schemas.BaseAnswer(attrs=attrs).dict())
        response = await auth_test_client.post(f"/answer/{factory_answer.survey_id}", json=answer)
        assert response.status_code == 409

    async def test_not_exists_survey(
            self,
            auth_test_client: AsyncClient,
            factory_survey: Survey
    ):
        attrs = await build_answer_attrs_with_survey_attrs(survey=factory_survey)
        answer = await serialize_uuid_to_str(schemas.BaseAnswer(attrs=attrs).dict())
        response = await auth_test_client.post(f"/answer/{uuid4()}", json=answer)
        assert response.status_code == 404

    async def test_without_user(
            self,
            factory_survey: Survey,
            test_client: AsyncClient,
    ):
        attrs = await build_answer_attrs_with_survey_attrs(survey=factory_survey)
        answer = await serialize_uuid_to_str(schemas.BaseAnswer(attrs=attrs).dict())
        response = await test_client.post(f"/answer/{factory_survey.id}", json=answer)
        assert response.status_code == 401
