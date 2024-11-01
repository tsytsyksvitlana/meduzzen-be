from sqlalchemy import Integer
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column
)


class Base(DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(self):
        return self.__name__

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
