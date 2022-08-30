import datetime
from functools import lru_cache
from pathlib import Path

from pydantic import BaseSettings, PostgresDsn, EmailStr

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    PROJECT_NAME: str
    SECRET_KEY: str
    SERVER_HOST: str
    BASE_APP_URI: str
    TOKEN_ENCODE_ALGORITHM = "HS256"
    ACCESS_TOKEN_JWT_SUBJECT = "access"
    PASSWORD_RESET_JWT_SUBJECT = "preset"

    SQL_ENGINE: str
    SQL_USER: str
    SQL_PASSWORD: str
    SQL_HOST: str
    SQL_PORT: str
    SQL_DATABASE: str

    EMAIL_RESET_TOKEN_EXPIRE = 48
    EMAIL_TEMPLATES_DIR: str
    EMAILS_FROM_EMAIL: EmailStr
    EMAIL_TEST_USER: EmailStr

    SMTP_TLS: bool
    SMTP_PORT: int
    SMTP_HOST: str
    SMTP_USER: EmailStr
    SMTP_PASSWORD: str

    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7

    ADMIN_FIXTURE_USERNAME: str
    ADMIN_FIXTURE_EMAIL: str
    ADMIN_FIXTURE_PASSWORD: str
    ADMIN_FIXTURE_FIRST_NAME: str
    ADMIN_FIXTURE_LAST_NAME: str
    ADMIN_FIXTURE_BIRTH_DATE: datetime.date
    ADMIN_FIXTURE_IS_ACTIVE: bool = True
    ADMIN_FIXTURE_IS_STUFF: bool = True
    ADMIN_FIXTURE_IS_SUPERUSER: bool = True

    @property
    def EMAIL_TEMPLATES_DIR(self) -> str:
        return str(Path(__file__).parent.parent / "email-templates/htmls")

    @property
    def EMAILS_ENABLED(self) -> str:
        return f"{self.SMTP_HOST}{self.SMTP_PORT}{self.EMAILS_FROM_EMAIL}"

    @property
    def EMAILS_FROM_NAME(self) -> str:
        return self.PROJECT_NAME

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return PostgresDsn.build(
            scheme=self.SQL_ENGINE,
            user=self.SQL_USER,
            password=self.SQL_PASSWORD,
            host=self.SQL_HOST,
            path=f"/{self.SQL_DATABASE}",
        )

    @property
    def BASE_APP_URI(self):
        return f"http://{self.SERVER_HOST}"

    class Config:
        env_file = Path(f"{BASE_DIR}/.env")


@lru_cache
def get_settings() -> Settings:
    return Settings()
