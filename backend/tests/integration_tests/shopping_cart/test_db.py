import pytest

from backend.src.schemas.recipes import ShoppingCartRecipeCreate


@pytest.mark.order(9)
async def test_shopping_cart_cd(db, test_recipe):
    recipe = test_recipe
    shopping_cart_recipe_data = ShoppingCartRecipeCreate(
        recipe_id=recipe.id, user_id=recipe.author.id
    )
    add_in_shopping_cart = await db.shopping_cart.create(shopping_cart_recipe_data)
    assert (
        add_in_shopping_cart.id == recipe.id
    ), "id рецепта не соответствует id рецепта в корзине"
    assert (
        add_in_shopping_cart.name == recipe.name
    ), "name рецепта не соответствует name рецепта в корзине"
    assert add_in_shopping_cart.cooking_time == recipe.cooking_time, (
        "cooking_time рецепта не соответствует " "cooking_time рецепта в корзине"
    )
    assert (
        add_in_shopping_cart.image == recipe.image
    ), "image рецепта не соответствует image рецепта в корзине"

    await db.shopping_cart.delete(
        recipe_id=add_in_shopping_cart.id, user_id=recipe.author.id
    )

    await db.recipes.delete(id=recipe.id)
    await db.commit()
