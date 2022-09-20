import datetime
from typing import List, Optional

from pydantic import BaseModel, constr, UUID4


class SurveyBase(BaseModel):
    name: constr(max_length=255)
    available: bool
    description: str

    class Config:
        allow_mutation = True
        orm_mode = True


class SurveyAttribure(BaseModel):
    question: str
    required: bool
    available: Optional[bool]

    class Config:
        allow_mutation = True
        orm_mode = True


class SurveyOut(SurveyBase):
    id: UUID4
    created_at: datetime.datetime


class SurveyCreate(SurveyBase):
    attrs: List[SurveyAttribure]


class SurveyAttributeRetrieve(SurveyAttribure):
    id: UUID4


class SurveyRetrieve(SurveyOut):
    attrs: List[SurveyAttributeRetrieve]


class SurveyUpdate(BaseModel):
    name: Optional[constr(max_length=255)]
    available: Optional[bool]
    description: Optional[bool]


class SurveyAttributeUpdate(BaseModel):
    question: Optional[str]
    required: Optional[bool]

