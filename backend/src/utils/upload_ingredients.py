import csv
import sys
from asyncio import run
from pathlib import Path

from sqlalchemy import insert

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from backend.src.base import IngredientModel # noqa
from backend.src.db_manager import DBManager
from backend.src.db import session, async_session_maker  # noqa


def ingredietns_to_add():
    with open('../data/ingredients.csv') as f:
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
        async with DBManager(session_factory=async_session_maker) as db:
            await db.session.execute(ingredients_stmt)
            await db.commit()
    run(implement_query())


if __name__ == '__main__':
    ingredietns_to_add()
