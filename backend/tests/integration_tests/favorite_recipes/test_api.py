from fastapi import status

recipe_id = 0


# @pytest.mark.order(12)
async def test_make_recipe_favorite(
    auth_ac,
    another_auth_ac,
    test_recipe,
    # removing_recipe_after_test,
    db,
):
    recipe = test_recipe
    favorite_recipe = await auth_ac.post(f"/api/recipes/{recipe.id}/favorite")
    assert (
        favorite_recipe.status_code == status.HTTP_201_CREATED
    ), "статус ответа отличается от 201"
    assert favorite_recipe.json()["id"] == recipe.id, "в ответе отсутствует поле id"
    assert (
        favorite_recipe.json()["name"] == recipe.name
    ), "в ответе отсутствует поле name"
    assert (
        favorite_recipe.json()["cooking_time"] == recipe.cooking_time
    ), "в ответе отсутствует поле cooking_time"
    assert (
        favorite_recipe.json()["image"] == recipe.image
    ), "в ответе отсутствует поле image"
    assert (
        len(favorite_recipe.json()) == 4
    ), "Корректные поля в ответе: id, name, cooking_time, image"
    delete_favorite_recipe = await auth_ac.delete(f"/api/recipes/{recipe.id}/favorite")
    assert (
        delete_favorite_recipe.status_code == status.HTTP_204_NO_CONTENT
    ), "статус ответа отличается от 204"
    await db.commit()


async def test_delete_favorite_recipe_by_another(another_auth_ac, test_recipe):
    delete_favorite_recipe_by_another_user = await another_auth_ac.delete(
        "/api/recipes/10/favorite"
    )
    print(delete_favorite_recipe_by_another_user.status_code)
    assert (
        delete_favorite_recipe_by_another_user.status_code
        == status.HTTP_400_BAD_REQUEST
    ), "статус ответа " "отличается от 400"
