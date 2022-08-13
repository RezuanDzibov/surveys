from datetime import datetime

from sqlalchemy import Column, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from models.base import Base, UUIDMixin


class Survey(UUIDMixin, Base):
    name = Column(String(length=255))
    created_at = Column(DateTime, default=datetime.now)
    attrs = relationship("Attribute")


class Attribute(UUIDMixin, Base):
    name = Column(String(length=255))
    question = Column(Text)
    required = Column(Boolean)
    answer = Column(Boolean)
    survey_id = Column(UUID, ForeignKey(Survey.id))
    survey = relationship("Survey", back_populates="attrs")

