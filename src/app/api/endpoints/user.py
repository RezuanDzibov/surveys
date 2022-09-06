from typing import List

from fastapi import APIRouter, Depends
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.db.base import get_session
from app.models.user import User
from app.schemas import user as user_schemas
from app.services import user as user_services

router = APIRouter()


@router.get("/me", response_model=user_schemas.UserRetrieve)
async def get_current_user(user: User = Depends(get_current_active_user)):
    return user


@router.patch("/me/update", response_model=user_schemas.UserRetrieve)
async def update_current_user(
    user_to_update: user_schemas.UserUpdate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
):
    user = await user_services.update_user(
        session=session,
        where_statements=[User.id == current_user.id],
        to_update=user_to_update.dict(exclude_none=True),
    )
    return user


@router.get("", response_model=List[user_schemas.UserList])
async def get_users(session: AsyncSession = Depends(get_session)):
    users = await user_services.get_users(session=session)
    return users


@router.get("/{user_id}", response_model=user_schemas.UserRetrieve)
async def get_user(user_id: UUID4, session: AsyncSession = Depends(get_session)):
    user = await user_services.get_user(session=session, where_statements=[User.id == user_id])
    return user
