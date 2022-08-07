from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import get_current_active_user
from db.base import get_session
from models.user import User
from schemas import user as user_schemas
from services import user as user_services

router = APIRouter()


@router.get("/me", response_model=user_schemas.UserRetrieve)
def get_current_user(user: dict = Depends(get_current_active_user)):
    return user


@router.patch("/me/update", response_model=user_schemas.UserRetrieve)
def update_current_user(
    user_to_update: user_schemas.UserUpdate,
    current_user: dict = Depends(get_current_active_user),
    session: Session = Depends(get_session),
):
    user = user_services.update_user(
        session=session,
        where_statements=[User.id == current_user.id],
        to_update=user_to_update.dict(exclude_none=True),
    )
    return user


@router.get("", response_model=list[user_schemas.UserList])
def get_users(session: Session = Depends(get_session)):
    users = user_services.get_users(session=session)
    return users
