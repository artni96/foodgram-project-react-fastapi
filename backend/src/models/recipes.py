from backend.src.db import Base
from sqlalchemy import String, Text, CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column
from backend.src.constants import PARAMS_MAX_LENGTH


class RecipeImageModel(Base):
    name: Mapped[str]
    base64: Mapped[str]


class RecipeModel(Base):
    author: Mapped[int] = mapped_column(
        ForeignKey('user.id', ondelete='cascade')
    )
    tag: Mapped[list["TagModel"]] = relationship(
        back_populates='recipe',
        secondary='recipetag'
    )
    name: Mapped[str] = mapped_column(String(PARAMS_MAX_LENGTH))
    text: Mapped[str] = mapped_column(Text)
    cooking_time: Mapped[int]
    image: Mapped[int] = mapped_column(
        ForeignKey('recipeimage.id')
    )
    image_obj = relationship('RecipeImageModel', backref='recipe')

    __table_args__ = (
        CheckConstraint(
            sqltext='cooking_time > 0',
            name='check_cooking_time_non_negative'
        ),
    )
