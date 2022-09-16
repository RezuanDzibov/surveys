from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.background import BackgroundTasks

from app.api.deps import get_current_active_user
from app.core.jwt import create_access_token
from app.db.base import get_session
from app.forms.auth import LoginForm
from app.models import User
from app.schemas.auth import Token, PasswordReset, PasswordChange
from app.schemas.base import Message
from app.schemas.user import UserRegistrationIn
from app.services import auth as auth_services
from app.services import user as user_services

router = APIRouter()


@router.post("/registration", response_model=Message)
async def registration(new_user: UserRegistrationIn, task: BackgroundTasks, session: AsyncSession = Depends(get_session)):
    await user_services.create_user(session=session, new_user=new_user, task=task)
    return Message(message="Verification email has just been sent.")


@router.post("/login/access-token", response_model=Token)
async def access_token(
    login_form: LoginForm = Depends(LoginForm),
    session: AsyncSession = Depends(get_session),
):
    user = await auth_services.authenticate(session=session, login=login_form.login, password=login_form.password)
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user.")
    return Token(**create_access_token(user.id))


@router.get("/confirm-registration/{verification_id}", response_model=Message)
async def confirm_registration(verification_id: UUID, session: AsyncSession = Depends(get_session)):
    await auth_services.verify_registration_user(session=session, verification_id=verification_id)
    return Message(message="Successfully verify email")


@router.get("/recover-password/{email}", response_model=Message)
async def recover_password(email: EmailStr, task: BackgroundTasks, session: AsyncSession = Depends(get_session)):
    await auth_services.recover_password(session=session, task=task, email=email)
    return Message(message="Recovery email has been sent.")


@router.post("/reset-password", response_model=Message)
async def reset_password(
    password_reset_data: PasswordReset,
    session: AsyncSession = Depends(get_session),
):
    await auth_services.reset_password(
        session=session,
        token=password_reset_data.reset_token,
        new_password=password_reset_data.new_password
    )
    return Message(message="Successfully recovered password.")


@router.patch("/change-password", response_model=Message)
async def change_password(
        password_change: PasswordChange,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_active_user)
):
    await user_services.change_user_password(session=session, password_change=password_change, user=current_user)
    return Message(message="Updated user password.")
