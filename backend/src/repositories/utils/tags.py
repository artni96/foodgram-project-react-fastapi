from backend.src.models.tags import TagModel
from backend.src.schemas.tags import RecipeTagCreate


async def recipe_tags(tags_data, db, recipe_id):
    recipe_tags_to_create: list[RecipeTagCreate] = list()
    for tag in tags_data:
        recipe_tags_to_create.append(
            RecipeTagCreate(
                recipe_id=recipe_id, tag_id=tag)
        )
    await db.recipe_tags.bulk_create(recipe_tags_to_create)
    tags_result = await db.tags.get_filtered(TagModel.id.in_(tags_data))
    return tags_result
