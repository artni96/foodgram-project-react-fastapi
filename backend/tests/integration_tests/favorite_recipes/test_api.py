import pytest
from fastapi import status


# @pytest.mark.order(12)
async def test_make_recipe_favorite_flow(
    auth_ac,
    another_auth_ac,
    test_recipe,
    # removing_recipe_after_test,
    db
):
    recipe = test_recipe
    favorite_recipe = await auth_ac.post(
        f'/api/recipes/{recipe.id}/favorite'
    )
    assert favorite_recipe.status_code == status.HTTP_201_CREATED, 'статус ответа отличается от 201'
    assert favorite_recipe.json()['id'] == recipe.id, 'в ответе отсутствует поле id'
    assert favorite_recipe.json()['name'] == recipe.name, 'в ответе отсутствует поле name'
    assert favorite_recipe.json()['cooking_time'] == recipe.cooking_time, 'в ответе отсутствует поле cooking_time'
    assert favorite_recipe.json()['image'] == recipe.image, 'в ответе отсутствует поле image'
    assert len(favorite_recipe.json()) == 4, 'Корректные поля в ответе: id, name, cooking_time, image'
    delete_favorite_recipe_by_another_user = await another_auth_ac.delete(
        f'/api/recipes/{recipe.id}/favorite'
    )
    assert delete_favorite_recipe_by_another_user.status_code == status.HTTP_400_BAD_REQUEST, ('статус ответа '
                                                                                               'отличается от 400')
    # print(recipe.id)
    delete_favorite_recipe = await auth_ac.delete(
        f'/api/recipes/{recipe.id}/favorite'
    )
    # print(delete_favorite_recipe)
    assert delete_favorite_recipe.status_code == status.HTTP_204_NO_CONTENT, 'статус ответа отличается от 204'

    assert (
            delete_favorite_recipe_by_another_user.json()['detail']
            == f'Рецепт с id {recipe.id} в избранном не найден.'
    )
    await db.recipes.delete(id=recipe.id)
    await db.commit()
