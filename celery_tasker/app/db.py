from datetime import datetime
from typing import Annotated

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, DeclarativeBase, declared_attr, mapped_column

from app.config import get_db_url


DATABASE_URL = get_db_url()
engine = create_engine(DATABASE_URL)
session_maker = sessionmaker(bind=engine)

int_pk = Annotated[int, mapped_column(primary_key=True)]
created_at = Annotated[datetime, mapped_column(server_default=func.now())]
updated_at = Annotated[
    datetime, mapped_column(server_default=func.now(), onupdate=func.now())
]
str_uniq = Annotated[str, mapped_column(unique=True, nullable=False)]
str_null_true = Annotated[str, mapped_column(nullable=True)]


class Base(DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"
