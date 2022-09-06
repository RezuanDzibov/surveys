import uuid
from typing import Any, TypeVar

from sqlalchemy import Column, inspect
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import NoInspectionAvailable
from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base:
    id: Any
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    def __eq__(self, other):
        if not self.__mapper__.class_ == other.__mapper__.class_:
            raise TypeError(f"{str(other)} is not {self.__class__} instance")
        for column in self.__table__.columns:
            if getattr(self, column.name) != getattr(other, column.name):
                return False
        return True

    def as_dict(self) -> dict:
        try:
            to_return: dict = inspect(self).dict
            for key, value in to_return.items():
                if isinstance(value, list) and value:
                    serialized_items = list()
                    for item in value:
                        if isinstance(item, Base):
                            serialized_items.append(item.as_dict())
                    to_return[key] = serialized_items
        except NoInspectionAvailable:
            to_return = self.__dict__
        if hasattr(self, "_sa_instance_state"):
            to_return.pop("_sa_instance_state")
        return to_return


class UUIDMixin:
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


BaseModel = TypeVar("BaseModel", bound=Base)
