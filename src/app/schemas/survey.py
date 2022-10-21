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


class SurveyOwnerRetrieve(SurveyRetrieve):
    available: bool


class SurveyUpdate(BaseModel):
    name: Optional[constr(max_length=255)]
    available: Optional[bool]
    description: Optional[str]


class SurveyAttributeUpdate(BaseModel):
    question: Optional[str]
    required: Optional[bool]


class SurveyFilter(BaseModel):
    name: Optional[constr(max_length=255)]
    description: Optional[str]


class SurveyDelete(SurveyOut):
    available: bool
