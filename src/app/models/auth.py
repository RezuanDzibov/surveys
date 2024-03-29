from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, backref

from .base import Base, UUIDMixin
from .user import User


class Verification(UUIDMixin, Base):
    user_id = Column(UUID(as_uuid=True), ForeignKey(User.id), nullable=False)
    user = relationship("User", backref=backref("verification_code", uselist=False))
