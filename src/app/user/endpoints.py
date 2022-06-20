from fastapi import APIRouter, Depends

from auth.permissions import get_current_active_user
from db.models.user import User
from user.schemas import UserRetrieve

router = APIRouter()


@router.get("/me", response_model=UserRetrieve)
def get_current_user(user: User = Depends(get_current_active_user)):
    return UserRetrieve.from_orm(user)
