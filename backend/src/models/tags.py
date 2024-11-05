import re

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, validates, relationship

from backend.src.constants import PARAMS_MAX_LENGTH
from backend.src.db import Base


class TagModel(Base):
    name: Mapped[str] = mapped_column(String(PARAMS_MAX_LENGTH))
    color: Mapped[str | None] = mapped_column(String(7))
    slug: Mapped[str | None] = mapped_column(
        String(PARAMS_MAX_LENGTH),
        unique=True
    )

    recipe: Mapped[list["RecipeModel"]] = relationship(
        back_populates='tag',
        secondary='recipetag'
    )

    @validates('slug')
    def validate_slug(self, key, value):
        pattern = '^[-a-zA-Z0-9_]+$'
        if not re.fullmatch(pattern=pattern, string=value):
            raise ValueError('Указанный слаг не удовлетворяет паттерну')
        return value


class RecipeTagModel(Base):
    tag_id: Mapped[int] = mapped_column(ForeignKey(
        'tag.id',
        ondelete='cascade',
        onupdate='cascade'
        )
    )
    recipe_id: Mapped[int] = mapped_column(ForeignKey(
        'recipe.id',
        ondelete='cascade',
        onupdate='cascade'
        )
    )
