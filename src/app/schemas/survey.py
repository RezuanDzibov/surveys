import datetime
from typing import List

from pydantic import BaseModel, constr, UUID4


class SurveyBase(BaseModel):
    name: constr(max_length=255)

    class Config:
        allow_mutation = True
        orm_mode = True


class SurveyAttribure(BaseModel):
    question: str
    required: bool

    class Config:
        allow_mutation = True
        orm_mode = True


class SurveyOut(SurveyBase):
    id: UUID4
    created_at: datetime.datetime


class SurveyCreate(SurveyBase):
    attrs: List[SurveyAttribure]
