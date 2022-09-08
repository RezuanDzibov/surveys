from datetime import datetime

from sqlalchemy import Column, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, UUIDMixin
from .user import User


class BaseAttribure:
    question = Column(Text)
    required = Column(Boolean)


class Survey(UUIDMixin, Base):
    name = Column(String(length=255))
    available = Column(Boolean)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    user_id = Column(UUID, ForeignKey(User.id), nullable=False)
    user = relationship("User", back_populates="surveys")
    attrs = relationship("SurveyAttribute")
    answers = relationship("Answer", back_populates="survey")


class Answer(UUIDMixin, Base):
    created_at = Column(DateTime, default=datetime.now)
    survey_id = Column(UUID, ForeignKey(Survey.id), nullable=False)
    survey = relationship("Survey", back_populates="answers")
    user_id = Column(UUID, ForeignKey(User.id), nullable=False)
    user = relationship("User", back_populates="answers")
    attrs = relationship("AnswerAttribute")


class SurveyAttribute(UUIDMixin, BaseAttribure, Base):
    survey_id = Column(UUID, ForeignKey(Survey.id), nullable=False)
    survey = relationship("Survey", back_populates="attrs")


class AnswerAttribute(UUIDMixin, BaseAttribure, Base):
    answer_id = Column(UUID, ForeignKey(Answer.id), nullable=False)
    answer = relationship("Answer", back_populates="attrs")
