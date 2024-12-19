from sqlalchemy import delete

from backend.src.models.tags import RecipeTagModel, TagModel
from backend.src.repositories.base import BaseRepository
from backend.src.schemas.tags import RecipeTagCreate, TagRead


class TagRepository(BaseRepository):
    model = TagModel
    schema = TagRead


class RecipeTagRepository(BaseRepository):
    model = RecipeTagModel

    async def create(self, tags_data, db, recipe_id):
        """Добавление тегов рецепту."""
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
        """Обновление тегов рецепта."""
        recipe_tags_to_delete_stmt = (
            delete(RecipeTagModel)
            .filter_by(recipe_id=recipe_id)
        )
        await self.session.execute(recipe_tags_to_delete_stmt)
        new_tags = await self.create(
            tags_data=tags_data,
            db=db,
            recipe_id=recipe_id
        )
        return new_tags
