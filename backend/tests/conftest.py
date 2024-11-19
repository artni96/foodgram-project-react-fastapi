import pytest
from backend.src.config import settings
from backend.src.db import engine, async_session_maker_null_pool
from backend.src.base import *
from backend.src.db_manager import DBManager
from backend.src.schemas.ingredients import IngredientCreate
import json


@pytest.fixture(scope='session', autouse=True)
async def check_test_mode():
    assert settings.MODE == 'TEST'


@pytest.fixture(scope='session', autouse=True)
async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    with open('tests/mock_ingredients.json', 'r') as file:
        ingredients = json.load(file)
    print(ingredients)

    ingredients_data = [IngredientCreate.model_validate(obj_data) for obj_data in ingredients]

    async with DBManager(session_factory=async_session_maker_null_pool) as _db:
        await _db.ingredients.bulk_create(ingredients_data)
        await _db.commit()
