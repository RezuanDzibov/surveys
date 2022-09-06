from typing import Optional, List

from fastapi.exceptions import HTTPException
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.background import BackgroundTasks

from app.core.emails import send_new_account_email
from app.core.security import get_password_hash, verify_password
from app.models import User
from app.schemas.auth import PasswordChange
from app.schemas.user import UserRegistrationIn
from app.services import auth as auth_services
from app.services import base as base_services


async def create_user(session: AsyncSession, new_user: UserRegistrationIn, task: BackgroundTasks) -> User:
    if new_user.password != new_user.password_repeat:
        raise HTTPException(status_code=400, detail="password and password_repeat doesn't match")
    statement = select(User).where(or_(User.username == new_user.username, User.email == new_user.email))
    is_object_exists = await base_services.is_object_exists(session=session, statement=statement)
    if is_object_exists:
        raise HTTPException(
            status_code=409,
            detail=f"User with username: {new_user.username} or email: {new_user.email} exists.",
        )
    new_user = new_user.dict()
    raw_password = new_user.pop("password_repeat")
    new_user["password"] = get_password_hash(raw_password)
    user = await base_services.insert_object(
        session=session,
        model=User,
        to_insert=new_user,
    )
    verification = await auth_services.create_verification(session=session, user_id=str(user.id))
    task.add_task(
        send_new_account_email,
        new_user.get("email"),
        new_user.get("username"),
        raw_password,
        str(verification.id),
    )
    return user


async def get_user(session: AsyncSession, where_statements: list) -> User:
    statement = select(User).where(*where_statements)
    user = await base_services.get_object(session=session, statement=statement)
    return user


async def update_user(
    session: AsyncSession,
    to_update: dict,
    where_statements: Optional[list] = None,
) -> User:
    user = await base_services.update_object(
        session=session,
        model=User,
        where_statements=where_statements,
        to_update=to_update,
    )
    return user


async def change_user_password(session: AsyncSession, password_change: PasswordChange, user: User) -> None:
    if not verify_password(password_change.current_password, user.passoword):
        raise HTTPException(
            status_code=400,
            detail="Provided password is incorrect",
        )
    if password_change.new_password == password_change.current_password:
        raise HTTPException(status_code=400, detail="New password can't be the same as current password.")
    if password_change.new_password != password_change.new_password_repeated:
        raise HTTPException(status_code=401, detail="new_password and new_password_repeated doesn't match.")
    await update_user(
        session=session,
        to_update={
            "password": get_password_hash(password=password_change.new_password)
        },
        where_statements=[User.id == user.id]
    )


async def get_users(session: AsyncSession) -> List[User]:
    users = await base_services.get_objects(session=session, model=User)
    return users
