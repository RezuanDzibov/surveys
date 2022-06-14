from typing import Union

from fastapi import Form
from pydantic import BaseModel, UUID4, EmailStr, constr


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    user_id: UUID4


class Message(BaseModel):
    message: str


class OAuth2TokenRequestForm(BaseModel):
    login: Union[constr(max_length=255), EmailStr]
    password: constr(max_length=255, min_length=8)

    @classmethod
    def as_form(
        cls,
        login: constr(max_length=255) = Form(...),
        password: constr(max_length=255, min_length=8) = Form(...),
    ):
        return cls(login=login, password=password)


class PasswordResetForm(BaseModel):
    token: str
    new_password: constr(max_length=255, min_length=8)

    @classmethod
    def as_form(
        cls,
        token: str = Form(...),
        new_password: constr(max_length=255, min_length=8) = Form(...),
    ):
        return cls(token=token, new_password=new_password)
