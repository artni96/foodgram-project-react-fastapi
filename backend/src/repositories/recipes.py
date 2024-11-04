from backend.src.repositories.base import BaseRepository
from backend.src.models.recipes import RecipeModel
from backend.src.schemas.recipes import RecipeRead
from sqlalchemy import select
from sqlalchemy.orm import selectinload


class RecipeRepository(BaseRepository):
    model = RecipeModel
    schema = RecipeRead

    async def get_one_or_none(self, id):
        recipe_stmt = (
            select(self.model)
            .filter_by(id=id)
            .options(selectinload(self.model.tag))
        )
        recipe_result = await self.session.execute(recipe_stmt)
        recipe_result = recipe_result.scalars().one_or_none()
        if recipe_result:
            return self.schema.model_validate(
                recipe_result,
                from_attributes=True
            )
