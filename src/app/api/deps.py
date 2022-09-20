from typing import Optional

from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.jwt import get_user_by_jwt_token
from app.core.settings import get_settings
from app.db.base import get_session
from app.models.user import User

settings = get_settings()

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/login/access-token")
optional_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/access-token", auto_error=False)


async def get_current_user(
        token: str = Security(reusable_oauth2),
        session: AsyncSession = Depends(get_session)
) -> User:
    return await get_user_by_jwt_token(token=token, session=session)


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


async def get_current_active_user_or_none(
        token: Optional[str] = Security(optional_oauth2_scheme),
        session: AsyncSession = Depends(get_session)
) -> Optional[User]:
    if token:
        return await get_user_by_jwt_token(token=token, session=session)
    return None
