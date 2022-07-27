from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP

from jinja2 import Environment, FileSystemLoader

from app.core.settings import get_settings

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
