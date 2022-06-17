from fastapi import APIRouter, Depends

from auth.permissions import get_user
from db.models.user import User
from user.schemas import BaseUser

user_router = APIRouter()


@user_router.get("/me", response_model=BaseUser)
def get_current_user(user: User = Depends(get_user)):
    return BaseUser.from_orm(user)
