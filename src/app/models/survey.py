from datetime import datetime

from sqlalchemy import Column, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, UUIDMixin
from .user import User


class Survey(UUIDMixin, Base):
    name = Column(String(length=255))
    available = Column(Boolean)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    user_id = Column(UUID(as_uuid=True), ForeignKey(User.id), nullable=False)
    user = relationship("User", back_populates="surveys")
    attrs = relationship("SurveyAttribute", passive_deletes=True)
    answers = relationship("Answer", back_populates="survey")


class Answer(UUIDMixin, Base):
    created_at = Column(DateTime, default=datetime.now)
    available = Column(Boolean)
    survey_id = Column(UUID(as_uuid=True), ForeignKey(Survey.id), nullable=False)
    survey = relationship("Survey", back_populates="answers")
    user_id = Column(UUID(as_uuid=True), ForeignKey(User.id), nullable=False)
    user = relationship("User", back_populates="answers")
    attrs = relationship("AnswerAttribute", passive_deletes=True)


class SurveyAttribute(UUIDMixin, Base):
    question = Column(Text)
    required = Column(Boolean)
    available = Column(Boolean, default=True)
    survey_id = Column(UUID(as_uuid=True), ForeignKey(Survey.id, ondelete="CASCADE"), nullable=False)
    survey = relationship("Survey", back_populates="attrs")
    answer_attrs = relationship("AnswerAttribute", passive_deletes=True)


class AnswerAttribute(UUIDMixin, Base):
    text = Column(String(length=255))
    survey_attr_id = Column(UUID(as_uuid=True), ForeignKey(SurveyAttribute.id, ondelete="CASCADE"), nullable=False)
    answer_id = Column(UUID(as_uuid=True), ForeignKey(Answer.id, ondelete="CASCADE"), nullable=False)
    answer = relationship("Answer", back_populates="attrs")
