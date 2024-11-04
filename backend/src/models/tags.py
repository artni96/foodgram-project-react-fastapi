from backend.src.db import Base
from sqlalchemy.orm import Mapped, mapped_column, validates
from sqlalchemy import String
import re


class TagModel(Base):
    name: Mapped[str] = mapped_column(String(200))
    color: Mapped[str | None] = mapped_column(String(7))
    slug: Mapped[str | None] = mapped_column(String(200), unique=True)

    @validates('slug')
    def validate_slug(self, key, value):
        pattern = '^[-a-zA-Z0-9_]+$'
        if not re.fullmatch(pattern=pattern, string=value):
            raise ValueError('Указанный слаг не удовлетворяет паттерну')
        return value
