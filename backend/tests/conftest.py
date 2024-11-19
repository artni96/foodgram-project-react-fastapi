import json

import pytest
from httpx import ASGITransport, AsyncClient

from backend.src.base import *
from backend.src.config import settings
from backend.src.db import engine, async_session_maker
from backend.src.db_manager import DBManager
from backend.src.schemas.ingredients import IngredientCreate
from backend.src.main import app
from fastapi import status


@pytest.fixture(scope='session', autouse=True)
async def check_test_mode():
    assert settings.MODE == 'TEST'


@pytest.fixture(scope='session', autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    with open('tests/mock_ingredients.json', 'r') as file:
        ingredients = json.load(file)
    ingredients_data = [IngredientCreate.model_validate(obj_data) for obj_data in ingredients]

    async with DBManager(session_factory=async_session_maker) as _db:
        await _db.ingredients.bulk_create(ingredients_data)
        await _db.commit()


@pytest.fixture(scope='session')
async def ac(setup_database):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope='session', autouse=True)
async def add_new_user(ac):
    new_user = await ac.post(
        "/api/users",
        json = {
            "email": "test_user_1@ya.net",
            "password": "string",
            "username": "test_user_1",
        })
    assert new_user.status_code == status.HTTP_201_CREATED


@pytest.fixture(scope='session')
async def auth_ac(ac):
    jwt_token = await ac.post(
        'api/users/token/login',
        data = {
            "username": "test_user_1@ya.net",
            "password": "string"
        }
    )
    assert jwt_token.status_code == status.HTTP_200_OK
    assert isinstance(jwt_token.json()['access_token'], str)
    async with AsyncClient(
        transport=ASGITransport(app=app),
            base_url="http://test",
            headers={'Authorization': f'Bearer {jwt_token.json()["access_token"]}'}) as ac:
        yield ac
