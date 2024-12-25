from backend.src.schemas.ingredients import IngredientRead
from backend.src.services.base import BaseService


class IngredientService(BaseService):
    async def get_ingredient_by_id(self, id: int) -> IngredientRead | None:
        return await self.db.ingredients.get_one_or_none(id=id)

    async def get_filtered_ingredients_by_name(
        self, name: str | None = None
    ) -> list[IngredientRead] | None:
        return await self.db.ingredients.get_filtered(name=name)
