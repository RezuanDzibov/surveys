from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.models.user import User
from app.db.session import get_session
from app.user import schemas
from app.user import services as user_services
from app.user.deps import get_current_active_user

router = APIRouter()


@router.get("/me", response_model=schemas.UserRetrieve)
def get_current_user(user: dict = Depends(get_current_active_user)):
    return user


@router.patch("/me/update", response_model=schemas.UserRetrieve)
def update_current_user(
    user_to_update: schemas.UserUpdate,
    current_user: dict = Depends(get_current_active_user),
    session: Session = Depends(get_session),
):
    user = user_services.update_user(
        session=session,
        where_statements=[User.id == current_user.get("id")],
        to_update=user_to_update.dict(exclude_none=True),
    )
    return user


@router.get("", response_model=list[schemas.UserList])
def get_users(session: Session = Depends(get_session)):
    users = user_services.get_users(session=session)
    return users
