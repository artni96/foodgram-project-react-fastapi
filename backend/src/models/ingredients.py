from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, UniqueConstraint, ForeignKey
from backend.src.constants import PARAMS_MAX_LENGTH

from backend.src.base import Base


class IngredientModel(Base):
    name: Mapped[str] = mapped_column(String(PARAMS_MAX_LENGTH))
    measurement_unit: Mapped[str] = mapped_column(String(PARAMS_MAX_LENGTH))

    __table_args__ = (
        UniqueConstraint(
            'name', 'measurement_unit', name='unique ingredients'
        ),
    )


class IngredientAmountModel(Base):
    ingredient_id: Mapped[int] = mapped_column(ForeignKey(
        'ingredient.id', ondelete='cascade', onupdate='cascade'
        )
    )
    amount: Mapped[int]


class RecipeIngredientModel(Base):
    ingredient_amount_id: Mapped[int] = mapped_column(ForeignKey(
        'ingredientamount.id', ondelete='cascade', onupdate='cascade'
        )
    )
    recipe_id: Mapped[int] = mapped_column(ForeignKey(
        'recipe.id', ondelete='cascade', onupdate='cascade'
        )
    )
