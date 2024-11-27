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
    assert make_recipe_favorite.id == recipe.id, 'id рецепта не соответствует id избранного рецепта'
    assert make_recipe_favorite.name == recipe.name, 'name рецепта не соответствует name избранного рецепта'
    assert make_recipe_favorite.cooking_time == recipe.cooking_time, 'id рецепта не соответствует id избранного рецепта'
    assert make_recipe_favorite.image == recipe.image, 'image рецепта не соответствует image избранного рецепта'

    await db.favorite_recipes.delete(recipe_id=make_recipe_favorite.id, user_id=recipe.author.id)

    await db.recipes.delete(id=recipe.id)
    await db.commit()
