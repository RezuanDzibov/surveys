from typing import Union

from fastapi import Form
from pydantic import constr, EmailStr


class LoginForm:
    def __init__(
        self,
        login: Union[constr(max_length=255), EmailStr] = Form(),
        password: constr(max_length=255, min_length=8) = Form()

    ):
        self.login = login
        self.password = password
