from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from starlette.background import BackgroundTasks
from sqlalchemy.orm import Session

from auth import services as auth_services
from auth.jwt import create_token
from auth.schemas import Token, OAuth2TokenRequestForm, PasswordResetForm
from db.session import get_session
from user import services as user_services
from user.schemas import UserRegistrationIn
from schemas import Message

router = APIRouter()


@router.post("/registration", response_model=Message)
def user_registration(new_user: UserRegistrationIn, task: BackgroundTasks, session: Session = Depends(get_session)):
    user_services.create_user(session=session, new_user=new_user, task=task)
    return Message(message="A verification email has just sent")


@router.post("/login/access-token", response_model=Token)
def user_access_token(
    form_data: OAuth2TokenRequestForm = Depends(OAuth2TokenRequestForm.as_form),
    session: Session = Depends(get_session),
):
    user = auth_services.authenticate(session=session, login=form_data.login, password=form_data.password)
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return create_token(user.id.hex)


@router.get("/confirm-email/{verification_uuid}", response_model=Message)
def confirm_email(verification_uuid: UUID, session: Session = Depends(get_session)):
    auth_services.verify_registration_user(session=session, verification_id=verification_uuid)
    return Message(message="Successfully verify email")


@router.post("/password-recovery/{email}", response_model=Message)
def recover_password(email: str, task: BackgroundTasks, session: Session = Depends(get_session)):
    auth_services.password_recover(session=session, task=task, email=email)
    return Message(message="The recovery email has been sent.")


@router.post("/reset-password", response_model=Message)
def reset_password(
    form: PasswordResetForm = Depends(PasswordResetForm.as_form),
    session: Session = Depends(get_session),
):
    auth_services.reset_password(session=session, token=form.token, new_password=form.new_password)
    return Message(message="Successfully recovered password.")
