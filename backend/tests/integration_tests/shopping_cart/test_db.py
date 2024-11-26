import pytest
from sqlalchemy import select

from backend.src.models.recipes import ShoppingCartModel
from backend.src.schemas.recipes import ShoppingCartRecipeCreate, RecipeCreateRequest


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
    shopping_cart_list_stmt = select(ShoppingCartModel)
    shopping_cart_list = await db.session.execute(shopping_cart_list_stmt)
    shopping_cart_list = shopping_cart_list.scalars().all()
    assert shopping_cart_list[-1].id == add_in_shopping_cart.id

    await db.shopping_cart.delete(recipe_id=recipe.id, user_id=recipe.author.id)
    await db.commit()

    await db.recipes.delete(id=recipe.id)
    await db.commit()
