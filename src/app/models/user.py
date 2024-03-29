from datetime import datetime

from sqlalchemy import Column, String, DATE, DateTime, Boolean
from sqlalchemy.orm import relationship

from .base import UUIDMixin, Base


class User(UUIDMixin, Base):
    username = Column(String(length=255), unique=True)
    email = Column(String(length=255), unique=True)
    password = Column(String(length=100))
    first_name = Column(String(length=100))
    last_name = Column(String(length=100))
    birth_date = Column(DATE)
    join_date_time = Column(DateTime, default=datetime.now)
    is_active = Column(Boolean, default=False)
    is_stuff = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    surveys = relationship("Survey", back_populates="user")
    answers = relationship("Answer", back_populates="user")
