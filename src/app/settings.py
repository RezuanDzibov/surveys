from pathlib import Path
from functools import lru_cache

from pydantic import BaseSettings, PostgresDsn, EmailStr

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    PROJECT_NAME: str
    SECRET_KEY: str
    SERVER_HOST: str

    SQL_ENGINE: str
    SQL_USER: str
    SQL_PASSWORD: str
    SQL_HOST: str
    SQL_PORT: str
    SQL_DATABASE: str

    EMAIL_RESET_TOKEN_EXPIRE = 48
    EMAIL_TEMPLATES_DIR = "email-templates/htmls"
    EMAILS_FROM_EMAIL: EmailStr
    EMAIL_TEST_USER: EmailStr

    SMTP_TLS: bool
    SMTP_PORT: str
    SMTP_HOST: str
    SMTP_USER: EmailStr
    SMTP_PASSWORD: str

    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7

    @property
    def EMAILS_ENABLED(self) -> str:
        return f"{self.SMTP_HOST}{self.SMTP_PORT}{self.EMAILS_FROM_EMAIL}"

    @property
    def EMAILS_FROM_NAME(self) -> str:
        return self.PROJECT_NAME

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme=self.SQL_ENGINE,
            user=self.SQL_USER,
            password=self.SQL_PASSWORD,
            host=self.SQL_HOST,
            path=f"/{self.SQL_DATABASE}",
        )

    class Config:
        env_file = Path(f"{BASE_DIR}/.env")


@lru_cache
def get_settings() -> Settings:
    return Settings()
