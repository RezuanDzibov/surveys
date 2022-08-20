from datetime import datetime

from sqlalchemy import Column, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, UUIDMixin
from .user import User


class BaseAttribure:
    name = Column(String(length=255))
    question = Column(Text)
    required = Column(Boolean)


class Survey(UUIDMixin, Base):
    name = Column(String(length=255))
    created_at = Column(DateTime, default=datetime.now)
    user_id = Column(UUID, ForeignKey(User.id))
    user = relationship("User", back_populates="surveys")
    attrs = relationship("SurveyAttribute")
    answers = relationship("Answer", back_populates="survey")


class Answer(UUIDMixin, Base):
    created_at = Column(DateTime, default=datetime.now)
    survey_id = Column(UUID, ForeignKey(Survey.id))
    survey = relationship("Survey", back_populates="answers")
    user_id = Column(UUID, ForeignKey(User.id))
    user = relationship("User", back_populates="answers")
    attrs = relationship("AnswerAttribute")


class SurveyAttribute(UUIDMixin, BaseAttribure, Base):
    survey_id = Column(UUID, ForeignKey(Survey.id))
    survey = relationship("Survey", back_populates="attrs")


class AnswerAttribute(UUIDMixin, BaseAttribure, Base):
    answer_id = Column(UUID, ForeignKey(Answer.id))
    answer = relationship("Answer", back_populates="attrs")
