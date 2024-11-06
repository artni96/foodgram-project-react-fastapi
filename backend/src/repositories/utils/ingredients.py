import csv
import sys
from asyncio import run
from pathlib import Path

from sqlalchemy import insert

sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))

from backend.src.base import IngredientModel  # noqa
from backend.src.db import session  # noqa
from backend.src.schemas.ingredients import (IngredientAmountCreate, # noqa
                                             RecipeIngredientAmountCreate,
                                             RecipeIngredientAmountRead)


def ingredietns_to_add():
    with open('data/ingredients.csv') as f:
        ingredients_file = csv.reader(f)
        ingredients_to_add = []
        for row in ingredients_file:
            current_obj = {
                'name': row[0],
                'measurement_unit': row[1]
            }
            ingredients_to_add.append(current_obj)

    async def implement_query():
        ingredients_stmt = insert(IngredientModel).values(ingredients_to_add)
        await session.execute(ingredients_stmt)
        await session.commit()
        await session.close()
    run(implement_query())


if __name__ == '__main__':
    ingredietns_to_add()


async def add_ingredients_to_recipe(ingredients_data, recipe_id, db):
    ingredients_amount_list_to_create: list[IngredientAmountCreate] = list()
    existing_ingredients_amount_ids: list[int] = list()
    ingredients_amount_list_response: list[RecipeIngredientAmountRead] = list()
    for obj in ingredients_data:
        current_ingredient_amount = (
            await db.ingredients_amount.get_one_or_none(
                ingredient_id=obj.id,
                amount=obj.amount)
        )
        if current_ingredient_amount:
            existing_ingredients_amount_ids.append(
                current_ingredient_amount.id)
        else:
            ingredients_amount_list_to_create.append(IngredientAmountCreate(
                ingredient_id=obj.id, amount=obj.amount))
        current_ingredient = await db.ingredients.get_one_or_none(id=obj.id)
        ingredients_amount_list_response.append(
            RecipeIngredientAmountRead(
                id=current_ingredient.id,
                name=current_ingredient.name,
                measurement_unit=current_ingredient.measurement_unit,
                amount=obj.amount
            )
         )
    if ingredients_amount_list_to_create:
        ingredients_amount_ids = await db.ingredients_amount.bulk_create(
            ingredients_amount_list_to_create
        )
        ingredients_amount_ids += existing_ingredients_amount_ids
    else:
        ingredients_amount_ids = existing_ingredients_amount_ids
    recipe_ingredients_amount_data = [
        RecipeIngredientAmountCreate(
            recipe_id=recipe_id,
            ingredient_amount_id=_id)
        for _id in ingredients_amount_ids
    ]
    await db.recipe_ingredient_amount.bulk_create(
        recipe_ingredients_amount_data
    )
    return ingredients_amount_list_response
