from pydantic import BaseModel


async def validate_filter(filter: BaseModel) -> dict:
    extracted_filter = filter.dict(exclude_none=True)
    return extracted_filter
