from datetime import datetime

from pydantic import BaseModel, constr, EmailStr, PastDate


class BaseUser(BaseModel):
    username: constr(max_length=255)
    email: EmailStr
    first_name: constr(max_length=100)
    last_name: constr(max_length=100)
    birth_date: PastDate
    join_date_time: datetime

    class Config:
        allow_mutation = True
        orm_mode = True


class UserRegistrationIn(BaseUser):
    password: constr(max_length=100, min_length=8)
