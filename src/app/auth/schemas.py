from typing import Union

from pydantic import BaseModel, UUID4, EmailStr, constr


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    user_id: UUID4


class Login(BaseModel):
    login: Union[constr(max_length=255), EmailStr]
    password: constr(max_length=255, min_length=8)


class PasswordReset(BaseModel):
    token: str
    new_password: constr(max_length=255, min_length=8)


class PasswordChange(BaseModel):
    current_password: constr(max_length=255, min_length=8)
    new_password: constr(max_length=255, min_length=8)
    new_password_repeated: constr(max_length=255, min_length=8)
