from typing import Optional

from fastapi.exceptions import HTTPException
from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from starlette.background import BackgroundTasks

import crud
from auth import services as auth_services
from auth.schemas import PasswordChange
from auth.security import get_password_hash, verify_password
from auth.send_email import send_new_account_email
from db.models.user import User
from user.schemas import UserRegistrationIn


def create_user(session: Session, new_user: UserRegistrationIn, task: BackgroundTasks) -> dict:
    statement = select(User).where(or_(User.username == new_user.username, User.email == new_user.email))
    is_object_exists = crud.is_object_exists(session=session, statement=statement)
    if is_object_exists:
        raise HTTPException(
            status_code=409,
            detail=f"User with username: {new_user.username} or email: {new_user.email} exists.",
        )
    raw_password = new_user.dict().pop("password")
    hash_password = get_password_hash(raw_password)
    new_user.password = hash_password
    user = crud.insert_object(
        session=session,
        model=User,
        to_insert=new_user.dict(),
    )
    verification = auth_services.create_verification(session=session, user_id=str(user.get("id")))
    task.add_task(
        send_new_account_email, new_user.email, new_user.username, raw_password, verification.get("id").hex,
    )
    return user


def get_user(session: Session, where_statements: list) -> dict:
    statement = select(User).where(*where_statements)
    user = crud.get_object(session=session, statement=statement)
    return user


def update_user(
    session: Session,
    to_update: dict,
    where_statements: Optional[list] = None,
) -> dict:
    user = crud.update_object(
        session=session,
        model=User,
        where_statements=where_statements,
        to_update=to_update,
    )
    return user


def change_user_password(session: Session, password_change: PasswordChange, user: dict) -> None:
    if not verify_password(password_change.current_password, user.get("password")):
        raise HTTPException(
            status_code=400,
            detail="Provided password is incorrect",
        )
    if password_change.new_password == password_change.current_password:
        raise HTTPException(status_code=400, detail="New password can't be the same as current password.")
    if password_change.new_password != password_change.new_password_repeated:
        raise HTTPException(status_code=401, detail="new_password and new_password_repeated doesn't match.")
    update_user(
        session=session,
        to_update={
            "password": get_password_hash(password=password_change.new_password)
        },
        where_statements=[User.id == user.get("id")]
    )
