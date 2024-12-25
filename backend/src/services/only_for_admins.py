from backend.src.schemas.ingredients import IngredientCreate, IngredientRead
from backend.src.schemas.tags import TagCreate, TagRead
from backend.src.services.base import BaseService


class OnlyForAdminService(BaseService):
    async def create_tag(self, data: TagCreate) -> TagRead:
        result = await self.db.tags.create(data=data)
        await self.db.commit()
        return result

    async def create_ingredient(self, data: IngredientCreate) -> IngredientRead:
        result = await self.db.ingredients.create(data=data)
        await self.db.commit()
        return result

    async def delete_tag(self, id: int) -> None:
        await self.db.tags.delete(id=id)
        await self.db.commit()

    async def delete_ingredient(self, id: int) -> None:
        await self.db.ingredients.delete(id=id)
        await self.db.commit()
