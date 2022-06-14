from pydantic import BaseModel, constr, EmailStr, PastDate


class UserRegistrationIn(BaseModel):
    username: constr(max_length=255)
    email: EmailStr
    password: constr(max_length=100, min_length=8)
    first_name: constr(max_length=100)
    last_name: constr(max_length=100)
    birth_date: PastDate

    class Config:
        mutable = True
