import csv
import sys
from asyncio import run
from pathlib import Path

from sqlalchemy import insert

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from backend.src.base import IngredientModel # noqa
from backend.src.db import session # noqa


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
