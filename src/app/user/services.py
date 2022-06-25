from typing import Optional

from fastapi.exceptions import HTTPException
from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from starlette.background import BackgroundTasks

import crud
from auth import services as auth_services
from auth.security import get_password_hash
from auth.send_email import send_new_account_email
from db.models.user import User
from user.schemas import UserRegistrationIn


def create_user(session: Session, new_user: UserRegistrationIn, task: BackgroundTasks) -> None:
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
        to_return=[User.id],
    )
    verification = auth_services.create_verification(session=session, user_id=str(user))
    task.add_task(
        send_new_account_email, new_user.email, new_user.username, raw_password, verification,
    )


def get_user(session: Session, where_statements: list) -> User:
    statement = select(User).where(*where_statements)
    user = crud.get_object(session=session, statement=statement)
    return user


def update_user(
    session: Session,
    to_update: dict,
    user_object_to_update: Optional[User] = None,
    where_statements: Optional[list] = None,
) -> User:
    if user_object_to_update:
        if isinstance(user_object_to_update, User):
            user = crud.update_object(
                session=session,
                object_=user_object_to_update,
                to_update=to_update,
            )
            return user
        raise TypeError("You've provided not an User instance.")
    if where_statements:
        user = crud.update_object_in_db(
            session=session,
            model=User,
            where_statements=where_statements,
            to_update=to_update,
        )
        return user
    raise AttributeError("You haven't provided user_to_update or where_statements,")
