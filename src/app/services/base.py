from typing import Optional, Type, Union, List

from asyncpg.exceptions import UniqueViolationError, ForeignKeyViolationError
from fastapi import HTTPException
from sqlalchemy import delete, exists, insert, update, select
from sqlalchemy.exc import NoResultFound, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Executable

from app.core.exceptions import raise_404
from app.models.base import BaseModel


async def is_object_exists(session: AsyncSession, statement: Executable) -> bool:
    statement = exists(statement).select()
    result = await session.execute(statement)
    is_exists = result.one()[0]
    return is_exists


async def update_object(
    session: AsyncSession,
    model: Type[BaseModel],
    where_statements: list[Executable],
    to_update: dict,
    return_object: Optional[dict] = True,
) -> Optional[Union[BaseModel, bool]]:
    statement = update(model).where(*where_statements).values(**to_update)
    if return_object:
        statement = statement.returning(model)
    result = await session.execute(statement)
    await session.commit()
    if return_object:
        try:
            object_ = model(**dict(result.one()))
            return object_
        except NoResultFound:
            await raise_404()
    return None


async def insert_object(
    session: AsyncSession,
    model: Type[BaseModel],
    to_insert: dict,
    return_object: Optional[bool] = True,
) -> Optional[BaseModel]:
    statement = insert(model).values(**to_insert)
    if return_object:
        statement = statement.returning(model)
    try:
        result = await session.execute(statement)
        await session.commit()
        if return_object:
            object_ = model(**dict(result.one()))
            return object_
        return None
    except IntegrityError as exception:
        if isinstance(exception.orig.__cause__, ForeignKeyViolationError):
            raise ForeignKeyViolationError from exception
        if isinstance(exception.orig.__cause__, UniqueViolationError):
            raise HTTPException(status_code=409, detail="Already exists")


async def delete_object(
    session: AsyncSession,
    model: Type[BaseModel],
    where_statements: list[Executable],
    return_object: bool = True,
) -> Optional[Union[BaseModel, bool]]:
    statement = delete(model).where(*where_statements).returning(model)
    result = await session.execute(statement)
    await session.commit()
    if return_object:
        try:
            object_ = model(**dict(result.one()))
            return object_
        except NoResultFound:
            await raise_404()
    return None


async def get_object(session: AsyncSession, statement: Executable) -> BaseModel:
    result = await session.execute(statement)
    try:
        object_ = result.one()[0]
        return object_
    except NoResultFound:
        await raise_404()


async def get_objects(session: AsyncSession, model: Type[BaseModel]) -> List[BaseModel]:
    statement = select(model).order_by(model.id)
    result = await session.execute(statement=statement)
    objects = result.scalars().all()
    return objects
