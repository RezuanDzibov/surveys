import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent.parent

PROJECT_NAME = os.getenv("PROJECT_NAME")
SERVER_HOST = os.getenv("SERVER_HOST", "127.0.0.1:8000")

dotenv_path = Path(f"{BASE_DIR}/.env")
load_dotenv(dotenv_path=dotenv_path)

SECRET_KEY = os.getenv("SECRET_KEY")


SQL_ENGINE = os.getenv("SQL_ENGINE")
SQL_USER = os.getenv("SQL_USER")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")
SQL_HOST = os.getenv("SQL_HOST")
SQL_PORT = os.getenv("SQL_PORT")
SQL_DATABASE = os.getenv("SQL_DATABASE")

EMAILS_FROM_NAME = PROJECT_NAME
EMAIL_RESET_TOKEN_EXPIRE = 48
EMAIL_TEMPLATES_DIR = "email-templates/htmls"

SMTP_TLS = bool(os.getenv("SMTP_TLS"))
SMTP_PORT = os.getenv("SMTP_PORT")
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
EMAILS_FROM_EMAIL = os.getenv("EMAILS_FROM_EMAIL")

EMAILS_ENABLED = f"{SMTP_HOST}{SMTP_PORT}{EMAILS_FROM_EMAIL}"
EMAIL_TEST_USER = os.getenv("EMAIL_TEST_USER")

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7
