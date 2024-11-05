from backend.src.schemas.tags import RecipeTagCreate


async def recipe_tags(tags_data, db, recipe_id):
    for tag in tags_data:
    recipe_tags = [RecipeTagCreate(
        recipe_id=recipe_id, tag_id=tag_id)
        for tag_id in tags_data
    ]
    tags_result = await db.recipe_tags.bulk_create(recipe_tags)
