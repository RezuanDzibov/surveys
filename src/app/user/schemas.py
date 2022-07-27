from typing import Optional

from pydantic import BaseModel, constr, EmailStr, PastDate, UUID4


class BaseUser(BaseModel):
    email: EmailStr
    username: constr(max_length=255)

    class Config:
        allow_mutation = True
        orm_mode = True


class UserList(BaseUser):
    id: UUID4


class UserRegistrationIn(BaseUser):
    password: constr(max_length=100, min_length=8)


class UserRetrieve(UserList, BaseUser):
    first_name: constr(max_length=100)
    last_name: constr(max_length=100)
    birth_date: PastDate


class UserUpdate(BaseModel):
    first_name: Optional[constr(max_length=100)]
    last_name: Optional[constr(max_length=100)]
    birth_date: Optional[PastDate]
