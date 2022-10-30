from fastapi import APIRouter, Depends
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.db.base import get_session
from app.models import User
from app.schemas.survey import BaseAnswer, AnswerCreateOut
from app.services import survey as services

router = APIRouter()


@router.post("/{survey_id}", status_code=201, response_model=AnswerCreateOut)
async def add_answer(
        survey_id: UUID4,
        answer: BaseAnswer,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_active_user)
):
    answer = await services.CreateAnswer(
        session=session,
        answer=answer,
        user_id=current_user.id,
        survey_id=survey_id
    ).execute()
    return answer


@router.delete("/{answer_id}", status_code=204)
async def delete_answer(
        answer_id: UUID4,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_active_user)
):
    await services.delete_answer(
        session=session,
        user=current_user,
        answer_id=answer_id

    )
