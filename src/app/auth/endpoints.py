from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.background import BackgroundTasks

from auth import services as auth_services
from auth.jwt import create_token
from auth.schemas import Token, Login, PasswordReset, PasswordChange
from db.session import get_session
from schemas import Message
from user import services as user_services
from user.deps import get_current_active_user
from user.schemas import UserRegistrationIn

router = APIRouter()


@router.post("/registration", response_model=Message)
def registration(new_user: UserRegistrationIn, task: BackgroundTasks, session: Session = Depends(get_session)):
    user_services.create_user(session=session, new_user=new_user, task=task)
    return Message(message="Verification email has just been sent.")


@router.post("/login/access-token", response_model=Token)
def access_token(
    login_data: Login,
    session: Session = Depends(get_session),
):
    user = auth_services.authenticate(session=session, login=login_data.login, password=login_data.password)
    if not user.get("is_active"):
        raise HTTPException(status_code=400, detail="Inactive user.")
    return Token(**create_token(user.get("id").hex))


@router.get("/confirm-registration/{verification_id}", response_model=Message)
def confirm_registration(verification_id: UUID, session: Session = Depends(get_session)):
    auth_services.verify_registration_user(session=session, verification_id=str(verification_id))
    return Message(message="Successfully verify email")


@router.get("/recover-password/{email}", response_model=Message)
def recover_password(email: str, task: BackgroundTasks, session: Session = Depends(get_session)):
    auth_services.recover_password(session=session, task=task, email=email)
    return Message(message="Recovery email has been sent.")


@router.post("/reset-password", response_model=Message)
def reset_password(
    password_reset_data: PasswordReset,
    session: Session = Depends(get_session),
):
    auth_services.reset_password(
        session=session,
        token=password_reset_data.token,
        new_password=password_reset_data.new_password
    )
    return Message(message="Successfully recovered password.")


@router.patch("/change-password", response_model=Message)
def change_password(
        password_change: PasswordChange,
        session: Session = Depends(get_session),
        user: dict = Depends(get_current_active_user)
):
    user_services.change_user_password(session=session, password_change=password_change, user=user)
    return Message(message="Updated user password.")
