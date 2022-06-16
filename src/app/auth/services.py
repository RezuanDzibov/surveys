from datetime import datetime, timedelta
from uuid import UUID

import jwt
from fastapi import BackgroundTasks, HTTPException
from sqlalchemy import select, or_
from sqlalchemy.orm import Load, Session

import crud
from auth.jwt import ALGORITHM
from auth.security import get_password_hash, verify_password
from auth.send_email import send_reset_password_email
from settings import get_settings
from db.models.auth import Verification
from db.models.user import User
from user import services as user_services

settings = get_settings()

password_reset_jwt_subject = "preset"


def authenticate(session: Session, login: str, password: str) -> User:
    statement = select(User).options(
        Load(User).load_only(User.password, User.is_active),
    )
    statement = statement.where(or_(User.username == login, User.email == login))
    user = crud.get_object(session=session, statement=statement)
    if user is None:
        raise HTTPException(
            status_code=404,
            detail=f"User with username or email: {login}. Not found.",
        )
    if not verify_password(password, user.password):
        raise HTTPException(
            status_code=400,
            detail="Provided password is incorrect",
        )
    return user


def create_verification(session: Session, user_id: str) -> Verification:
    verification = crud.insert_object(
        session=session,
        model=Verification,
        to_insert={"user_id": user_id},
        returning=[Verification.id],
    )
    return verification


def verify_registration_user(session: Session, verification_id: UUID) -> None:
    statement = select(Verification).where(Verification.id == verification_id)
    verification = crud.get_object(session=session, statement=statement)
    if verification:
        user_services.update_user(
            session=session,
            where_statements=[User.id == verification.user_id],
            to_update={"is_active": True},
        )
        crud.delete_object(
            session=session,
            model=Verification,
            where_statements=[Verification.id == verification_id],
        )
    else:
        raise HTTPException(status_code=404, detail="Not found")


def password_recover(session: Session, task: BackgroundTasks, email: str) -> None:
    user = user_services.get_user(session=session, where_statements=[User.email == email])
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"The user with this email: {email} does not exist in the system.",
        )
    password_reset_token = generate_password_reset_token(email)
    task.add_task(
        send_reset_password_email, username=user.username, email=email, token=password_reset_token
    )


def generate_password_reset_token(email: str) -> str:
    delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE)
    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": password_reset_jwt_subject, "email": email},
        settings.SECRET_KEY,
        algorithm=ALGORITHM,
    )
    return encoded_jwt


def verify_password_reset_token(token: str) -> str:
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded_token["sub"] == password_reset_jwt_subject
        return decoded_token["email"]
    except jwt.InvalidTokenError:
        return None


def reset_password(session: Session, token: str, new_password: str) -> None:
    email = verify_password_reset_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = user_services.get_user(session=session, where_statements=[User.email == email])
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"The user with this email: {email} does not exist in the system.",
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    password_hash = get_password_hash(new_password)
    crud.update_model_instance(
        session=session,
        object_=user,
        to_update={"password": password_hash},
    )
