import typing

from sqlalchemy import CheckConstraint, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.src.constants import PARAMS_MAX_LENGTH
from backend.src.db import Base

if typing.TYPE_CHECKING:
    from backend.src.models.ingredients import IngredientAmountModel
    from backend.src.models.users import UserModel
    from backend.src.models.tags import TagModel


class ImageModel(Base):
    name: Mapped[str]
    base64: Mapped[str]
    recipe: Mapped[list["RecipeModel"]] = relationship(back_populates="image_info")


class RecipeModel(Base):
    author: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="cascade"))
    tags: Mapped[list["TagModel"]] = relationship(
        secondary="recipetag",
        back_populates="recipe",
    )
    name: Mapped[str] = mapped_column(String(PARAMS_MAX_LENGTH))
    text: Mapped[str] = mapped_column(Text)
    cooking_time: Mapped[int]
    image: Mapped[int] = mapped_column(ForeignKey("image.id"))
    ingredient_amount: Mapped[list["IngredientAmountModel"]] = relationship(
        secondary="recipeingredient", back_populates="recipe"
    )
    author_info: Mapped["UserModel"] = relationship(back_populates="recipe")
    is_favorited: Mapped[list["FavoriteRecipeModel"]] = relationship(
        back_populates="recipe"
    )
    is_in_shopping_cart: Mapped[list["ShoppingCartModel"]] = relationship(
        back_populates="recipe"
    )
    image_info: Mapped["ImageModel"] = relationship(back_populates="recipe")

    __table_args__ = (
        CheckConstraint(
            sqltext="cooking_time > 0", name="check_cooking_time_non_negative"
        ),
    )


class UserRecipeBaseModel(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="cascade"))
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipe.id", ondelete="cascade"))

    __abstract__ = True


class FavoriteRecipeModel(UserRecipeBaseModel):
    recipe: Mapped["RecipeModel"] = relationship(back_populates="is_favorited")
    __table_args__ = (
        UniqueConstraint("user_id", "recipe_id", name="unique favorite recipe"),
    )


class ShoppingCartModel(UserRecipeBaseModel):
    recipe: Mapped["RecipeModel"] = relationship(back_populates="is_in_shopping_cart")
    __table_args__ = (
        UniqueConstraint("user_id", "recipe_id", name="unique recipe in shopping cart"),
    )
