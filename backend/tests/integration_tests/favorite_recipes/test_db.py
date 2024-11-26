import pytest

from backend.src.schemas.recipes import FavoriteRecipeCreate


@pytest.mark.order(11)
async def test_favorite_recipes_cd(
    db,
    test_recipe
):
    recipe = test_recipe
    favorite_recipe_data = FavoriteRecipeCreate(
        recipe_id = recipe.id,
        user_id=recipe.author.id
    )
    make_recipe_favorite = await db.favorite_recipes.create(
        favorite_recipe_data
    )
    await db.commit()

    await db.favorite_recipes.delete(recipe_id=make_recipe_favorite.id, user_id=recipe.author.id)
    await db.commit()

    await db.recipes.delete(id=recipe.id)
    await db.commit()
