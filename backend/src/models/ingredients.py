from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, UniqueConstraint, ForeignKey, Integer

from backend.src.base import Base


class IngredientModel(Base):
    name: Mapped[str] = mapped_column(String(200))
    measurement_unit: Mapped[str] = mapped_column(String(200))

    __table_args__ = (
        UniqueConstraint(
            'name', 'measurement_unit', name='unique ingredients'
        ),
    )


# class IngredientAmountModel(Base):
#     ingredient_id: int = ForeignKey('ingredient.id')
#     amount: int = Integer()


# class RecipeIngredientModel(Base):
#     ingredient_amount_id: int = ForeignKey('ingredientamount.id')
#     recipe_id: int = ForeignKey('recipe.id')
