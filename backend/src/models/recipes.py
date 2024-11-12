from sqlalchemy import (CheckConstraint, ForeignKey, String, Text,
                        UniqueConstraint)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.src.constants import PARAMS_MAX_LENGTH
from backend.src.db import Base


class ImageModel(Base):
    name: Mapped[str]
    base64: Mapped[str]


class RecipeModel(Base):
    author: Mapped[int] = mapped_column(
        ForeignKey('user.id', ondelete='cascade')
    )
    tags: Mapped[list["TagModel"]] = relationship(
        secondary='recipetag',
        back_populates='recipe',
    )
    name: Mapped[str] = mapped_column(String(PARAMS_MAX_LENGTH))
    text: Mapped[str] = mapped_column(Text)
    cooking_time: Mapped[int]
    image: Mapped[int] = mapped_column(
        ForeignKey('image.id')
    )
    ingredient_amount: Mapped[list['IngredientAmountModel']] = relationship(
        secondary="recipeingredient",
        back_populates="recipe"
    )
    author_info: Mapped['UserModel'] = relationship(back_populates='recipe')

    __table_args__ = (
        CheckConstraint(
            sqltext='cooking_time > 0',
            name='check_cooking_time_non_negative'
        ),
    )


class UserRecipeBaseModel(Base):
    user_id: Mapped[int] = mapped_column(
        ForeignKey('user.id', ondelete='cascade')
    )
    recipe_id: Mapped[int] = mapped_column(
        ForeignKey('recipe.id', ondelete='cascade')
    )

    __abstract__ = True


class FavoriteRecipeModel(UserRecipeBaseModel):
    __table_args__ = (
        UniqueConstraint(
            'user_id',
            'recipe_id',
            name='unique favorite recipe'
        ),
    )


class ShoppingCartModel(UserRecipeBaseModel):
    __table_args__ = (
        UniqueConstraint(
            'user_id',
            'recipe_id',
            name='unique recipe in shopping cart'
        ),
    )
