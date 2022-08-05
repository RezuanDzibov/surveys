from datetime import datetime, timedelta

import jwt

from core.settings import get_settings

settings = get_settings()


def create_access_token(user_id: str) -> dict:
    access_token_expires = timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_jwt_token(
            data={"user_id": user_id}, expires_delta=access_token_expires
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
