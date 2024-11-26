import pytest

from backend.src.schemas.recipes import ShoppingCartRecipeCreate


@pytest.mark.order(9)
async def test_shopping_cart_cd(
    db,
    test_recipe
):
    recipe = test_recipe
    shopping_cart_recipe_data = ShoppingCartRecipeCreate(
        recipe_id = recipe.id,
        user_id=recipe.author.id
    )
    add_in_shopping_cart = await db.shopping_cart.create(
        shopping_cart_recipe_data
    )
    await db.commit()

    await db.shopping_cart.delete(recipe_id=add_in_shopping_cart.id, user_id=recipe.author.id)
    await db.commit()

    await db.recipes.delete(id=recipe.id)
    await db.commit()
