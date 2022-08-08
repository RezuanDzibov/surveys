import asyncio
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from core.security import get_password_hash
from core.settings import get_settings
from db.base import get_session
from models import User
from services import base as base_services

settings = get_settings()


def get_admin_user_data() -> dict:
    return {
        "username": settings.ADMIN_FIXTURE_USERNAME,
        "email": settings.ADMIN_FIXTURE_EMAIL,
        "password": settings.ADMIN_FIXTURE_PASSWORD,
        "first_name": settings.ADMIN_FIXTURE_FIRST_NAME,
        "last_name": settings.ADMIN_FIXTURE_LAST_NAME,
        "birth_date": settings.ADMIN_FIXTURE_BIRTH_DATE,
        "is_active": settings.ADMIN_FIXTURE_IS_ACTIVE,
        "is_stuff": settings.ADMIN_FIXTURE_IS_STUFF,
        "is_superuser": settings.ADMIN_FIXTURE_IS_SUPERUSER,
    }


async def create_admin_user(
    session: AsyncSession,
    to_insert: Optional[dict] = None,
    data_to_replace: Optional[dict] = None
) -> User:
    if not to_insert:
        to_insert = get_admin_user_data()
        if data_to_replace:
            for key, value in data_to_replace.items():
                if key in to_insert:
                    to_insert[key] = value
        to_insert["password"] = get_password_hash(to_insert.get("password"))
    user = await base_services.insert_object(
        session=session,
        model=User,
        to_insert=to_insert,
    )
    return user


async def main() -> None:
    session = anext(await get_session())
    await create_admin_user(session=session)


if __name__ == "__main__":
    asyncio.run(main())
