from fastapi import HTTPException


async def raise_404() -> None:
    raise HTTPException(status_code=404, detail="Not found")
