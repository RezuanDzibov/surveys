import jwt
from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError
from sqlalchemy.orm import Session
from starlette.status import HTTP_403_FORBIDDEN

from auth.schemas import TokenPayload
from settings import get_settings
from db.models.user import User
from db.session import get_session
from user import services as user_services

settings = get_settings()

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/login/access-token")


def get_current_user(token: str = Security(reusable_oauth2), session: Session = Depends(get_session)) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.TOKEN_ENCODE_ALGORITHM])
        token_data = TokenPayload(**payload)
    except PyJWTError:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials.",
        )
    user = user_services.get_user(session=session, where_statements=[User.id == token_data.user_id])
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user


def get_current_active_user(current_user: dict = Security(get_current_user)) -> dict:
    if not current_user.get("is_active"):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_superuser(current_user: dict = Security(get_current_active_user)) -> dict:
    if not current_user.get("is_superuser"):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges",
        )
    return current_user
