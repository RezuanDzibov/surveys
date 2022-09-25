import datetime
from typing import List, Optional

from pydantic import BaseModel, constr, UUID4


class SurveyBase(BaseModel):
    name: constr(max_length=255)
    description: str

    class Config:
        allow_mutation = True
        orm_mode = True


class SurveyAttribute(BaseModel):
    question: str
    required: bool
    available: Optional[bool]

    class Config:
        allow_mutation = True
        orm_mode = True


class SurveyOut(SurveyBase):
    id: UUID4
    created_at: datetime.datetime
    user_id: UUID4


class SurveyCreate(SurveyBase):
    available: bool
    attrs: List[SurveyAttribute]


class SurveyAttributeRetrieve(SurveyAttribute):
    id: UUID4
    available: bool


class SurveyRetrieve(SurveyOut):
    attrs: List[SurveyAttributeRetrieve]


class SurveyUpdate(BaseModel):
    name: Optional[constr(max_length=255)]
    available: Optional[bool]
    description: Optional[bool]


class SurveyAttributeUpdate(BaseModel):
    question: Optional[str]
    required: Optional[bool]

