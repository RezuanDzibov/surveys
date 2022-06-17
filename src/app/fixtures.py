import crud
from auth.security import get_password_hash
from db.models import User
from db.session import get_session


def create_initial_user() -> None:
    session = next(get_session())
    crud.insert_object(
        session=session,
        model=User,
        to_insert={
            "username": "rezuandzibov",
            "email": "rezuan.dzbov@gmail.com",
            "password": get_password_hash("somepass"),
            "first_name": "Rezuan",
            "last_name": "Dzibov",
            "birth_date": "2010-06-14",
            "is_active": True,
            "is_staff": True,
            "is_superuser": True,
        },
        returning=[],
    )


if __name__ == "__main__":
    create_initial_user()
