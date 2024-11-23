from backend.src.schemas.recipes import RecipeCreateRequest, RecipeUpdateRequest


async def test_recipe_crud(
        db,
        recipe_creation_fixture: RecipeCreateRequest,
        recipe_updating_fixture: RecipeUpdateRequest
):
    new_recipe = await db.recipes.create(recipe_data=recipe_creation_fixture,db=db, current_user_id=1)
    await db.commit()
    assert new_recipe.name == recipe_creation_fixture.name
    assert new_recipe.text == recipe_creation_fixture.text
    assert new_recipe.cooking_time == recipe_creation_fixture.cooking_time
    assert isinstance(new_recipe.cooking_time, int)
    assert isinstance(new_recipe.image, str)
    assert await db.recipes.check_recipe_exists(id=new_recipe.id)

    updated_recipe = await db.recipes.update(recipe_data=recipe_updating_fixture, id=new_recipe.id, db=db)
    await db.commit()
    assert updated_recipe.name == recipe_updating_fixture.name
    assert updated_recipe.text == recipe_updating_fixture.text
    assert updated_recipe.cooking_time == recipe_updating_fixture.cooking_time
    total_test_ingredient_amount = sum([ing.amount for ing in recipe_updating_fixture.ingredients])
    assert updated_recipe.ingredients[0].amount == total_test_ingredient_amount
    assert  await db.recipes.check_recipe_exists(id=updated_recipe.id)

    await db.recipes.delete(id=updated_recipe.id)
    await db.commit()

    assert not await db.recipes.check_recipe_exists(id=updated_recipe.id)
