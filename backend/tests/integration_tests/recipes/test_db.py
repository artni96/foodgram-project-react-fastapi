from backend.src.schemas.recipes import RecipeCreateRequest, RecipeUpdateRequest


async def test_recipe_crud(
    db,
    recipe_creation_fixture: RecipeCreateRequest,
    recipe_updating_fixture: RecipeUpdateRequest,
):
    new_recipe = await db.recipes.create(
        recipe_data=recipe_creation_fixture, db=db, current_user_id=1
    )
    await db.commit()
    assert (
        new_recipe.name == recipe_creation_fixture.name
    ), "значение name рецепта отличается от исходных данных"
    assert (
        new_recipe.text == recipe_creation_fixture.text
    ), "значение text рецепта отличается от исходных данных"
    assert new_recipe.cooking_time == recipe_creation_fixture.cooking_time, (
        "значение cooking_time рецепта " "отличается от исходных данных"
    )
    assert isinstance(
        new_recipe.cooking_time, int
    ), "валидный тип поля cooking_time - int"
    assert isinstance(new_recipe.image, str), "валидный тип поля cooking_time - str"
    assert await db.recipes.check_recipe_exists(
        id=new_recipe.id
    ), "новый рецепт не найден в БД"

    updated_recipe = await db.recipes.update(
        recipe_data=recipe_updating_fixture, id=new_recipe.id, db=db
    )
    await db.commit()
    assert updated_recipe.name == recipe_updating_fixture.name, (
        "значение name обновленного рецепта отличается от " "исходных данных"
    )
    assert updated_recipe.text == recipe_updating_fixture.text, (
        "значение text обновленного рецепта отличается от " "исходных данных"
    )
    assert updated_recipe.cooking_time == recipe_updating_fixture.cooking_time, (
        "значение cooking_time рецепта " "отличается от исходных данных"
    )
    total_test_ingredient_amount = sum(
        [ing.amount for ing in recipe_updating_fixture.ingredients]
    )
    assert (
        updated_recipe.ingredients[0].amount == total_test_ingredient_amount
    ), "неверное значение поля ingredients"
    assert await db.recipes.check_recipe_exists(
        id=updated_recipe.id
    ), "обновленный репецт не найден в бд"
    await db.recipes.delete(id=updated_recipe.id)
    await db.commit()
