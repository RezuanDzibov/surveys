from core.emails import send_email
from core.settings import get_settings

settings = get_settings()


def send_new_account_email(email_to: str, username: str, password: str, uuid: str) -> None:
    verification_link = f"{settings.BASE_APP_URI}/api/{settings.API_VERSION}/auth/confirm-registration/{uuid}"
    subject = "New user."
    send_email(
        email_to=email_to,
        template_name="new_account.html",
        subject=subject,
        environment={
            "project_name": settings.PROJECT_NAME,
            "username": username,
            "password": password,
            "email": email_to,
            "link": verification_link,
        },
    )


def send_reset_password_email(username: str, email: str, token: str) -> None:
    if hasattr(token, "decode"):
        use_token = token.decode()
    else:
        use_token = token
    subject = f"Password recovery for user {username}."
    send_email(
        email_to=email,
        template_name="reset_password.html",
        subject=subject,
        environment={
            "project_name": settings.PROJECT_NAME,
            "username": username,
            "email": email,
            "valid_minutes": settings.EMAIL_RESET_TOKEN_EXPIRE,
            "token": use_token,
        },
    )
