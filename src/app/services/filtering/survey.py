from typing import List

from sqlalchemy import column, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Survey
from app.schemas.survey import SurveyFilter
from app.services.filtering.common import validate_filter


async def filter_surveys(session: AsyncSession, filter: SurveyFilter) -> list | List[Survey]:
    validated_filter = await validate_filter(filter=filter)
    columns = [column(column_name).contains(column_value) for column_name, column_value in validated_filter.items()]
    statement = select(Survey).where(*columns)
    result = await session.execute(statement)
    surveys = result.scalars().all()
    return surveys

