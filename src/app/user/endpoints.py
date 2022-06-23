from fastapi import APIRouter, Depends

import crud
from auth.permissions import get_current_active_user
from db.models.user import User
from db.session import get_session
from user.schemas import UserRetrieve, UserUpdate
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/me", response_model=UserRetrieve)
def get_current_user(user: User = Depends(get_current_active_user)):
    return UserRetrieve.from_orm(user)


@router.patch("/me/update", response_model=UserRetrieve)
def update_current_user(
    user_to_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
):
    user = crud.update_object(
        session=session,
        object_=current_user,
        to_update=user_to_update.dict(exclude_none=True),
    )
    return UserRetrieve.from_orm(user)
