from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import BackgroundTasks, HTTPException
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.emails import send_reset_password_email
from app.core.security import get_password_hash, verify_password
from app.core.settings import get_settings
from app.models.auth import Verification
from app.models.user import User
from app.services import base as base_services
from app.services import user as user_services

settings = get_settings()


async def authenticate(session: AsyncSession, login: str, password: str) -> User:
    statement = select(User).where(or_(User.username == login, User.email == login))
    user = await base_services.get_object(session=session, statement=statement)
    if not verify_password(password, user.password):
        raise HTTPException(
            status_code=400,
            detail="Provided password is incorrect",
        )
    return user


async def create_verification(session: AsyncSession, user_id: str) -> Verification:
    verification = await base_services.insert_object(
        session=session,
        model=Verification,
        to_insert={"user_id": user_id},
    )
    return verification


async def verify_registration_user(session: AsyncSession, verification_id: str) -> None:
    statement = select(Verification).where(Verification.id == verification_id)
    verification = await base_services.get_object(session=session, statement=statement)
    await user_services.update_user(
        session=session,
        where_statements=[User.id == verification.user_id],
        to_update={"is_active": True},
    )
    await base_services.delete_object(
        session=session,
        model=Verification,
        where_statements=[Verification.id == verification_id],
        return_object=False,
    )


async def recover_password(session: AsyncSession, task: BackgroundTasks, email: str) -> str:
    user = await user_services.get_user(session=session, where_statements=[User.email == email])
    password_reset_token = generate_password_reset_token(email)
    task.add_task(
        send_reset_password_email, username=user.username, email=email, token=password_reset_token
    )
    return password_reset_token


def generate_password_reset_token(email: str) -> str:
    delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE)
    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": settings.PASSWORD_RESET_JWT_SUBJECT, "email": email},
        settings.SECRET_KEY,
        algorithm=settings.TOKEN_ENCODE_ALGORITHM,
    )
    return encoded_jwt


def verify_password_reset_token(token: str) -> Optional[str]:
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.TOKEN_ENCODE_ALGORITHM])
        assert decoded_token["sub"] == settings.PASSWORD_RESET_JWT_SUBJECT
        return decoded_token["email"]
    except jwt.InvalidTokenError:
        return None


async def reset_password(session: AsyncSession, token: str, new_password: str) -> User:
    email = verify_password_reset_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = await user_services.get_user(session=session, where_statements=[User.email == email])
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    password_hash = get_password_hash(new_password)
    user = await base_services.update_object(
        session=session,
        where_statements=[User.id == user.id],
        model=User,
        to_update={"password": password_hash},
    )
    return user
