from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import BackgroundTasks, HTTPException
from sqlalchemy import select, or_
from sqlalchemy.orm import Load, Session

from app import crud
from app.auth.security import get_password_hash, verify_password
from app.auth.send_email import send_reset_password_email
from app.db.models.auth import Verification
from app.db.models.user import User
from app.settings import get_settings
from app.user import services as user_services

settings = get_settings()


def authenticate(session: Session, login: str, password: str) -> dict:
    statement = select(User).options(
        Load(User).load_only(User.password, User.is_active),
    )
    statement = statement.where(or_(User.username == login, User.email == login))
    user = crud.get_object(session=session, statement=statement)
    if not verify_password(password, user.get("password")):
        raise HTTPException(
            status_code=400,
            detail="Provided password is incorrect",
        )
    return user


def create_verification(session: Session, user_id: str) -> dict:
    verification = crud.insert_object(
        session=session,
        model=Verification,
        to_insert={"user_id": user_id},
    )
    return verification


def verify_registration_user(session: Session, verification_id: str) -> None:
    statement = select(Verification).where(Verification.id == verification_id)
    verification = crud.get_object(session=session, statement=statement)
    user_services.update_user(
        session=session,
        where_statements=[User.id == verification.get("user_id")],
        to_update={"is_active": True},
    )
    crud.delete_object(
        session=session,
        model=Verification,
        where_statements=[Verification.id == verification_id],
        return_object=False,
    )


def recover_password(session: Session, task: BackgroundTasks, email: str) -> str:
    user = user_services.get_user(session=session, where_statements=[User.email == email])
    password_reset_token = generate_password_reset_token(email)
    task.add_task(
        send_reset_password_email, username=user.get("username"), email=email, token=password_reset_token
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


def reset_password(session: Session, token: str, new_password: str) -> dict:
    email = verify_password_reset_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = user_services.get_user(session=session, where_statements=[User.email == email])
    if not user.get("is_active"):
        raise HTTPException(status_code=400, detail="Inactive user")
    password_hash = get_password_hash(new_password)
    user = crud.update_object(
        session=session,
        where_statements=[User.id == user.get("id")],
        model=User,
        to_update={"password": password_hash},
    )
    return user
