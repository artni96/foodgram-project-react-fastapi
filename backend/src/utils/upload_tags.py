import csv
import sys
from asyncio import run
from pathlib import Path

from sqlalchemy import insert

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from backend.src.base import TagModel
from backend.src.db_manager import DBManager
from backend.src.db import async_session_maker


def tags_to_add():
    with open('./data/tags.csv') as f:
        tags_file = csv.reader(f)
        tags_list_to_add = []
        for row in tags_file:
            current_obj = {
                'name': row[0],
                'color': row[1],
                'slug': row[2]
            }
            tags_list_to_add.append(current_obj)

    async def implement_query():
        ingredients_stmt = insert(TagModel).values(tags_list_to_add)
        async with DBManager(session_factory=async_session_maker) as db:
            await db.session.execute(ingredients_stmt)
            await db.commit()
    run(implement_query())


if __name__ == '__main__':
    tags_to_add()
