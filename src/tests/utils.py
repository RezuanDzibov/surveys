from typing import List

from app.models import Survey
from tests.factories import AnswerAttributeFactory


async def build_answer_attrs_with_survey_attrs(survey: Survey) -> List[dict]:
    attrs = list()
    for survey_attr, answer_attr in zip(survey.attrs,
                                        AnswerAttributeFactory.build_batch(len(survey.attrs))):
        answer_attr.survey_attr_id = str(survey_attr.id)
        attrs.append(answer_attr.as_dict())
    return attrs
