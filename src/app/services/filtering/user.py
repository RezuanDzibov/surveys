from typing import List

from sqlalchemy import select, column
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.schemas.user import UserFilter
from app.services.filtering.common import validate_filter


async def filter_users(session: AsyncSession, filter: UserFilter) -> List[User]:
    validated_filter = await validate_filter(filter=filter)
    columns = [column(column_name).contains(column_value) for column_name, column_value in validated_filter.items()]
    statement = select(User).where(*columns)
    result = await session.execute(statement)
    users = result.scalars().all()
    return users
