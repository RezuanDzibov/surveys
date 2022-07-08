from typing import Optional, Type, Union, List

from fastapi import HTTPException
from psycopg2.errors import ForeignKeyViolation, UniqueViolation
from sqlalchemy import delete, exists, insert, update
from sqlalchemy.exc import NoResultFound, IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.sql import Executable

from db.utils import orm_row_to_dict
from db.models.base import Base


def is_object_exists(session: Session, statement: Executable) -> bool:
    statement = exists(statement).select()
    result = session.execute(statement)
    is_object_exists = result.one()[0]
    return is_object_exists


def update_object(
    session: Session,
    model: Type[Base],
    where_statements: List[Executable],
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
            raise HTTPException(status_code=404, detail="Not found")
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
    try:
        result = session.execute(statement)
        session.commit()
        if return_object:
            object_ = dict(result.one())
            return object_
        return None
    except IntegrityError as exception:
        if isinstance(exception.orig, ForeignKeyViolation):
            raise ForeignKeyViolation from exception
        elif isinstance(exception.orig, UniqueViolation):
            raise HTTPException(status_code=409, detail="Already exists")


def delete_object(
    session: Session,
    model: Type[Base],
    where_statements: List[Executable],
    return_object: bool = True,
) -> Optional[Union[dict, bool]]:
    statement = delete(model).where(*where_statements).returning(model)
    result = session.execute(statement)
    session.commit()
    if return_object:
        try:
            object_ = dict(result.one())
            return object_
        except NoResultFound:
            raise HTTPException(status_code=404, detail="Not found")
    return None


def get_object(session: Session, statement: Executable) -> Optional[dict]:
    result = session.execute(statement)
    try:
        object_ = orm_row_to_dict(result.one())
        return object_
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Not found")
