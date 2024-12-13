import os

from fastapi import status


async def test_shopping_cart_flow(
    auth_ac,
    another_auth_ac,
    test_recipe,
    db
):
    recipe = test_recipe
    recipe_to_shopping_cart = await auth_ac.post(
        f'/api/recipes/{recipe.id}/shopping_cart'
    )
    assert recipe_to_shopping_cart.status_code == status.HTTP_201_CREATED, 'статус ответа отличается от 201'
    assert recipe_to_shopping_cart.json()['id'] == recipe.id, 'в ответе отсутствует поле id'
    assert recipe_to_shopping_cart.json()['name'] == recipe.name, 'в ответе отсутствует поле name'
    assert (
        recipe_to_shopping_cart.json()['cooking_time']
        == recipe.cooking_time
    ), 'в ответе отсутствует поле cooking_time'
    assert recipe_to_shopping_cart.json()['image'] == recipe.image, 'в ответе отсутствует поле image'

    recipe_from_shopping_cart_by_another = await another_auth_ac.delete(
        f'/api/recipes/{recipe.id}/shopping_cart'
    )
    assert recipe_from_shopping_cart_by_another.status_code == status.HTTP_400_BAD_REQUEST

    recipe_from_shopping_cart = await auth_ac.delete(
        f'/api/recipes/{recipe.id}/shopping_cart'
    )
    assert recipe_from_shopping_cart.status_code == status.HTTP_204_NO_CONTENT, ('один пользователь не может удалять '
                                                                                 'рецепты из корзины другого '
                                                                                 'пользователя')
    await db.recipes.delete(id=recipe.id)
    await db.commit()

    download_shopping_cart = await auth_ac.get(
        '/api/recipes/download_shopping_cart'
    )
    assert download_shopping_cart.status_code == status.HTTP_200_OK, 'статус ответа отличается от 200'
    pdf_to_delete = (
        download_shopping_cart.headers['content-disposition'].split('filename=')[1]
    )

    pdf_path_to_delete = f'src/media/shopping_cart/shopping_lists/{pdf_to_delete}'
    assert os.path.exists(pdf_path_to_delete)
    os.remove(pdf_path_to_delete)
    assert not os.path.exists(pdf_path_to_delete)
