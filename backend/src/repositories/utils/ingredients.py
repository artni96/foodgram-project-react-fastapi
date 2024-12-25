import csv
import sys
from asyncio import run
from pathlib import Path

from sqlalchemy import insert

sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))

from backend.src.base import IngredientModel  # noqa
from backend.src.db import session  # noqa
from backend.src.schemas.ingredients import IngredientAmountCreate  # noqa


def upload_ingredietns():
    with open("data/ingredients.csv") as f:
        ingredients_file = csv.reader(f)
        ingredients_to_add = []
        for row in ingredients_file:
            current_obj = {"name": row[0], "measurement_unit": row[1]}
            ingredients_to_add.append(current_obj)

    async def implement_query():
        ingredients_stmt = insert(IngredientModel).values(ingredients_to_add)
        await session.execute(ingredients_stmt)
        await session.commit()
        await session.close()

    run(implement_query())


if __name__ == "__main__":
    upload_ingredietns()


async def check_ingredient_duplicates_for_recipe(ingredients_data):
    _ingredients_data = []
    ingredient_ids = [obj.id for obj in ingredients_data]
    if len(ingredient_ids) != set(ingredient_ids):
        for ingredient_id in set(ingredient_ids):
            current_ingredient = IngredientAmountCreate(
                ingredient_id=ingredient_id, amount=0
            )
            for ingredient_amount in ingredients_data:
                if ingredient_amount.id == ingredient_id:
                    current_ingredient.amount += ingredient_amount.amount
            _ingredients_data.append(current_ingredient)
        return _ingredients_data
    return ingredients_data
