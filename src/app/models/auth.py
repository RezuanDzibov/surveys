from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, backref

from models.base import Base, UUIDMixin
from models.user import User


class Verification(UUIDMixin, Base):
    user_id = Column(UUID, ForeignKey(User.id))
    user = relationship("User", backref=backref("verification_code", uselist=False))
