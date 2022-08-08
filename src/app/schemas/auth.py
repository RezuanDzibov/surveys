from pydantic import BaseModel, UUID4, constr


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    user_id: UUID4


class PasswordReset(BaseModel):
    reset_token: str
    new_password: constr(max_length=255, min_length=8)


class PasswordChange(BaseModel):
    current_password: constr(max_length=255, min_length=8)
    new_password: constr(max_length=255, min_length=8)
    new_password_repeated: constr(max_length=255, min_length=8)
