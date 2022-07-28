from typing import Optional

from sqlalchemy.orm import Session

from core.security import get_password_hash
from core.settings import get_settings
from db.base import get_session
from models import User
from services import base as base_services

settings = get_settings()


def get_initial_admin_user() -> dict:
    return {
        "username": settings.ADMIN_FIXTURE_USERNAME,
        "email": settings.ADMIN_FIXTURE_EMAIL,
        "password": get_password_hash(settings.ADMIN_FIXTURE_PASSWORD),
        "first_name": settings.ADMIN_FIXTURE_FIRST_NAME,
        "last_name": settings.ADMIN_FIXTURE_LAST_NAME,
        "birth_date": settings.ADMIN_FIXTURE_BIRTH_DATE,
        "is_active": settings.ADMIN_FIXTURE_IS_ACTIVE,
        "is_stuff": settings.ADMIN_FIXTURE_IS_STUFF,
        "is_superuser": settings.ADMIN_FIXTURE_IS_SUPERUSER,
    }


def create_admin_user(
    session: Session,
    to_insert: Optional[dict] = None,
    data_to_replace: Optional[dict] = None
) -> User:
    if not to_insert:
        to_insert = get_initial_admin_user()
        if data_to_replace:
            for key, value in data_to_replace.items():
                if key in to_insert:
                    to_insert[key] = value
    user = base_services.insert_object(
        session=session,
        model=User,
        to_insert=to_insert,
    )
    return user


if __name__ == "__main__":
    session = next(get_session())
    create_admin_user(session=session)
