from datetime import datetime, timedelta
from uuid import UUID

import jwt
from fastapi import HTTPException
from jwt import PyJWTError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_403_FORBIDDEN

from app.core.settings import get_settings
from app.models import User
from app.schemas.auth import TokenPayload
from app.services import user as user_services

settings = get_settings()


def create_access_token(user_id: UUID) -> dict:
    access_token_expires = timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_jwt_token(
            data={"user_id": str(user_id)}, expires_delta=access_token_expires
        ),
        "token_type": "Bearer",
    }


def create_jwt_token(*, data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire, "sub": settings.ACCESS_TOKEN_JWT_SUBJECT})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.TOKEN_ENCODE_ALGORITHM)
    return encoded_jwt


async def get_user_by_jwt_token(token: str, session: AsyncSession) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.TOKEN_ENCODE_ALGORITHM])
        token_data = TokenPayload(**payload)
    except PyJWTError:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials.",
        )
    user = await user_services.get_user(session=session, where_statements=[User.id == token_data.user_id])
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user
