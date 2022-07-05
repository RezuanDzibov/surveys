from typing import Optional, Type, Union

from sqlalchemy import delete, exists, insert, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from db.utils import orm_row_to_dict
from db.models.base import Base


def is_object_exists(session: Session, statement) -> bool:
    statement = exists(statement).select()
    result = session.execute(statement)
    is_object_exists = result.scalar()
    return is_object_exists


def update_object(
    session: Session,
    model: Type[Base],
    where_statements: list,
    to_update: dict,
    return_object: Optional[dict] = True,
) -> Optional[Union[dict, bool]]:
    statement = update(model).where(*where_statements).values(**to_update)
    if return_object:
        statement = statement.returning(model)
    result = session.execute(statement)
    session.commit()
    if return_object:
        try:
            object_ = dict(result.one())
            return object_
        except NoResultFound:
            return False
    return None


def insert_object(
    session: Session,
    model: Type[Base],
    to_insert: dict,
    return_object: Optional[bool] = True,
) -> Optional[dict]:
    statement = insert(model).values(**to_insert)
    if return_object:
        statement = statement.returning(model)
    result = session.execute(statement)
    session.commit()
    if return_object:
        object_ = dict(result.one())
        return object_
    return None


def delete_object(
    session: Session,
    model: Type[Base],
    where_statements: list,
    return_object: bool = True,
) -> Optional[dict]:
    statement = delete(model).where(*where_statements).returning(model)
    result = session.execute(statement)
    session.commit()
    if return_object:
        object_ = orm_row_to_dict(result.one())
        return object_
    return None


def get_object(session: Session, statement) -> Optional[dict]:
    result = session.execute(statement)
    try:
        object_ = orm_row_to_dict(result.one())
        return object_
    except NoResultFound:
        return None
