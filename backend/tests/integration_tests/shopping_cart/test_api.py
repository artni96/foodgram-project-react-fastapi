from fastapi import status


async def test_shopping_cart_flow(
    auth_ac,
    another_auth_ac,
    test_recipe
):
    recipe = test_recipe
    recipe_to_shopping_cart = await auth_ac.post(
        f'/api/recipes/{recipe.id}/shopping_cart'
    )
    assert recipe_to_shopping_cart.status_code == status.HTTP_201_CREATED
    assert recipe_to_shopping_cart.json()['id'] == recipe.id
    assert recipe_to_shopping_cart.json()['name'] == recipe.name
    assert (
        recipe_to_shopping_cart.json()['cooking_time']
        == recipe.cooking_time
    )
    assert recipe_to_shopping_cart.json()['image'] == recipe.image

    recipe_from_shopping_cart_by_another = await another_auth_ac.delete(
        f'/api/recipes/{recipe.id}/shopping_cart'
    )
    assert recipe_from_shopping_cart_by_another.status_code == status.HTTP_400_BAD_REQUEST

    recipe_from_shopping_cart = await auth_ac.delete(
        f'/api/recipes/{recipe.id}/shopping_cart'
    )
    assert recipe_from_shopping_cart.status_code == status.HTTP_204_NO_CONTENT
