from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP

from jinja2 import Environment, FileSystemLoader

from core.settings import get_settings

settings = get_settings()


def send_email(email_to: str, subject: str, template_name: str, environment: dict) -> None:
    env = Environment(loader=FileSystemLoader(settings.EMAIL_TEMPLATES_DIR))
    template = env.get_template(template_name)
    output = template.render(environment)
    from_email = settings.SMTP_USER
    message = MIMEMultipart()
    message["Subject"] = subject
    message["From"] = from_email
    message["To"] = email_to
    message.attach(MIMEText(output, "html"))
    message_body = message.as_string()
    with SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as smtp_server:
        smtp_server.starttls()
        smtp_server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        smtp_server.sendmail(from_email, email_to, message_body)


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
