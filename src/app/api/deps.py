import jwt
from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_403_FORBIDDEN

from app.core.settings import get_settings
from app.db.base import get_session
from app.models.user import User
from app.schemas.auth import TokenPayload
from app.services import user as user_services

settings = get_settings()

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/login/access-token")


async def get_current_user(token: str = Security(reusable_oauth2), session: AsyncSession = Depends(get_session)) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.TOKEN_ENCODE_ALGORITHM])
        token_data = TokenPayload(**payload)
    except PyJWTError:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials.",
        )
    user = await user_services.get_user(session=session, where_statements=[User.id == token_data.user_id])
    return user


async def get_current_active_user(current_user: User = Security(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_superuser(current_user: User = Security(get_current_active_user)) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges",
        )
    return current_user
