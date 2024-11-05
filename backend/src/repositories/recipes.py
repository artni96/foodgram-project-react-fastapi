from pydantic import BaseModel
from sqlalchemy import select, insert
from sqlalchemy.orm import selectinload

from backend.src.models.recipes import RecipeModel
from backend.src.repositories.base import BaseRepository
from backend.src.schemas.recipes import RecipeWithTagsRead


class RecipeRepository(BaseRepository):
    model = RecipeModel
    schema = RecipeWithTagsRead

    async def get_one_or_none(self, recipe_id, current_user_id, db):
        recipe_stmt = (
            select(self.model)
            .filter_by(id=recipe_id)
            .options(selectinload(self.model.tag))
        )

        recipe_result = await self.session.execute(recipe_stmt)
        recipe_result = recipe_result.scalars().one_or_none()
        user_result = await db.users.get_one_or_none(
            user_id=recipe_result.author,
            current_user_id=current_user_id
        )
        if recipe_result:
            return self.schema(
                author=user_result,
                name=recipe_result.name,
                text=recipe_result.text,
                cooking_time=recipe_result.cooking_time,
                tag=recipe_result.tag,
                id=recipe_result.id
            )

    async def create(self, data: BaseModel):
        new_obj_stmt = (
            insert(self.model)
            .values(**data.model_dump())
            .returning(self.model.id)
        )
        result = await self.session.execute(new_obj_stmt)
        result = result.scalars().one()
        return result
