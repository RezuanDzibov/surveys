from typing import Optional

from pydantic import BaseModel, constr, EmailStr, PastDate, UUID4


class BaseUser(BaseModel):
    username: constr(max_length=255)
    first_name: constr(max_length=100)
    last_name: constr(max_length=100)
    birth_date: PastDate

    class Config:
        allow_mutation = True
        orm_mode = True


class UserRegistrationIn(BaseUser):
    email: EmailStr
    password: constr(max_length=100, min_length=8)


class UserRetrieve(BaseUser):
    id: UUID4
    email: EmailStr


class UserUpdate(BaseUser):
    username: Optional[constr(max_length=255)]
    first_name: Optional[constr(max_length=100)]
    last_name: Optional[constr(max_length=100)]
    birth_date: Optional[PastDate]
