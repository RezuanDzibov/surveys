from typing import Optional

from sqlalchemy import delete, exists, insert, update
from sqlalchemy.orm import Session

from db.models.base import Base


def is_object_exists(session: Session, statement) -> bool:
    statement = exists(statement).select()
    result = session.execute(statement)
    is_object_exists = result.scalar()
    return is_object_exists


def update_object(session: Session, object_: Base, to_update: dict) -> Base:
    for column_name, column_value in to_update.items():
        if not hasattr(object_, column_name):
            raise AttributeError(f"The object has no column {column_name}")
        setattr(object_, column_name, column_value)
    session.add(object_)
    session.commit()
    session.refresh(object_)
    return object_


def update_object_in_db(
    session: Session,
    model: Base,
    where_statements: list,
    to_update: dict,
    to_return: Optional[list] = None,
) -> Optional[Base]:
    statement = update(model).where(*where_statements).values(**to_update)
    if to_return:
        statement = statement.returning(*to_return)
    result = session.execute(statement)
    session.commit()
    if to_return:
        object_ = result.scalar()
        return object_
    return None


def insert_object(
    session: Session,
    model: Base,
    to_insert: dict,
    to_return: Optional[list] = None,
) -> Optional[Base]:
    statement = insert(model).values(**to_insert)
    if to_return:
        statement = statement.returning(*to_return)
    result = session.execute(statement)
    session.commit()
    if to_return:
        object_ = result.scalar()
        return object_
    return None


def delete_object(
    session: Session,
    model: Base,
    where_statements: list,
    to_return: list = None,
) -> Optional[Base]:
    statement = delete(model).where(*where_statements).returning(*to_return)
    result = session.execute(statement)
    session.commit()
    if to_return:
        object_ = result.scalar()
        return object_
    return None


def get_object(session: Session, statement) -> Base:
    result = session.execute(statement)
    object_ = result.scalar()
    return object_
