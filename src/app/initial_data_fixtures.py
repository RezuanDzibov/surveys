from app import crud
from app.auth.security import get_password_hash
from app.db.models import User
from app.db.session import get_session
from app.settings import get_settings

settings = get_settings()


def create_admin_user() -> dict:
    session = next(get_session())
    user = crud.insert_object(
        session=session,
        model=User,
        to_insert={
            "username": settings.ADMIN_FIXTURE_USERNAME,
            "email": settings.ADMIN_FIXTURE_EMAIL,
            "password": get_password_hash(settings.ADMIN_FIXTURE_PASSWORD),
            "first_name": settings.ADMIN_FIXTURE_FIRST_NAME,
            "last_name": settings.ADMIN_FIXTURE_LAST_NAME,
            "birth_date": settings.ADMIN_FIXTURE_BIRTH_DATE,
            "is_active": settings.ADMIN_FIXTURE_IS_ACTIVE,
            "is_staff": settings.ADMIN_FIXTURE_IS_STUFF,
            "is_superuser": settings.ADMIN_FIXTURE_IS_SUPERUSER,
        },
    )
    return user


if __name__ == "__main__":
    create_admin_user()
