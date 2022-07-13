from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, backref

from app.db.models.base import Base, UUIDMixin
from app.db.models.user import User


class Verification(UUIDMixin, Base):
    user_id = Column(UUID, ForeignKey(User.id))
    user = relationship("User", backref=backref("verification_code", uselist=False))
