from pydantic import BaseModel
from sqlalchemy import insert, select

from backend.src.base import IngredientAmountModel, IngredientModel, RecipeIngredientModel
from backend.src.repositories.base import BaseRepository
from backend.src.schemas.ingredients import (IngredientAmountRead,
                                             IngredientAmountCreate,
                                             IngredientRead)


class IngredientRepository(BaseRepository):
    model = IngredientModel
    schema = IngredientRead

    async def get_filtered(self, name: str | None):
        filtered_ingredients_stmt = select(self.model)
        if name:
            filtered_ingredients_stmt = (
                filtered_ingredients_stmt.filter(
                    self.model.name.startswith(name.lower())
                )
            )
        filtered_ingredients = await self.session.execute(
            filtered_ingredients_stmt
        )
        filtered_ingredients = filtered_ingredients.scalars().all()
        return [
            self.schema.model_validate(obj, from_attributes=True)
            for obj in filtered_ingredients
        ]


class IngredientAmountRepository(BaseRepository):
    model = IngredientAmountModel
    schema = IngredientAmountRead


class RecipeIngredientAmountRepository(BaseRepository):
    model = RecipeIngredientModel
    # schema = 