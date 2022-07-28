from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from core.settings import get_settings

settings = get_settings()


engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
