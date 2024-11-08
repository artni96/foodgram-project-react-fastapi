from backend.src.repositories.base import BaseRepository
from backend.src.models.tags import TagModel, RecipeTagModel
from backend.src.schemas.tags import TagRead, RecipeTagCreate
from pydantic import BaseModel
from sqlalchemy import insert, select


class TagRepository(BaseRepository):
    model = TagModel
    schema = TagRead


class RecipeTagRepository(BaseRepository):
    model = RecipeTagModel

    async def create(self, tags_data, db, recipe_id):
        recipe_tags_to_create: list[RecipeTagCreate] = list()
        for tag in tags_data:
            recipe_tags_to_create.append(
                RecipeTagCreate(
                    recipe_id=recipe_id, tag_id=tag)
            )
        await db.recipe_tags.bulk_create(recipe_tags_to_create)
        tags_result = await db.tags.get_filtered(TagModel.id.in_(tags_data))
        return tags_result

    async def update(self, tags_data, db, recipe_id):
        recipe_tags_to_delete_stmt = (
            select(RecipeTagModel.id)
            .filter_by(recipe_id=recipe_id)
        )
        await self.session.execute(recipe_tags_to_delete_stmt)
        new_tags = self.create_recipe_tags(
            tags_data=tags_data,
            db=db,
            recipe_id=recipe_id
        )
        return new_tags
