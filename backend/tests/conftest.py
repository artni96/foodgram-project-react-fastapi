import json
import pathlib

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import True_, select

from backend.src.base import *
from backend.src.config import settings
from backend.src.constants import MOUNT_PATH
from backend.src.db import engine, async_session_maker
from backend.src.db_manager import DBManager
from backend.src.models.recipes import ImageModel
from backend.src.schemas.ingredients import IngredientCreate, IngredientAmountCreate
from backend.src.main import app
from fastapi import status

from backend.src.schemas.recipes import RecipeCreateRequest, RecipeUpdateRequest
from backend.src.schemas.tags import TagCreate
import os


MAX_EMAIL_LENGTH = 254
USER_PARAMS_MAX_LENGTH = 150
PARAMS_MAX_LENGTH = 200


@pytest.fixture(scope='session', autouse=True)
async def check_test_mode():
    assert settings.MODE == 'TEST'


@pytest.fixture(scope='session', autouse=True)
async def setup_database():
    async with engine.connect() as conn:
        media_path = pathlib.Path(__file__).parent.parent.resolve()
        images_to_del_stmt = select(ImageModel.name)
        image_list = await conn.execute(images_to_del_stmt)
        image_list = image_list.scalars().all()
        print(image_list)
        for image in image_list:
            image_to_delete = (
                f'{media_path}/src{MOUNT_PATH}/{image}'
            )
            print(image_to_delete)
            if os.path.exists(image_to_delete):
                os.remove(image_to_delete)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    with open('tests/mock_ingredients.json', 'r') as file:
        ingredients = json.load(file)
    ingredients_data = [IngredientCreate.model_validate(obj_data) for obj_data in ingredients]

    async with DBManager(session_factory=async_session_maker) as _db:
        await _db.ingredients.bulk_create(ingredients_data)
        await _db.commit()


@pytest.fixture(autouse=True)
async def db():
    async with DBManager(session_factory=async_session_maker) as db:
        yield db

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

@pytest.fixture()
async def tags_fixture(db):
    tags_data = [
        {
            "name": "Завтрак",
            "color": "#f5945c",
            "slug": "breakfast"
        },
        {
            "name": "Обед",
            "color": "#75ba75",
            "slug": "lunch"
        },
        {
            "name": "Ужин",
            "color": "#be95be",
            "slug": "dinner"
        }
    ]
    tags_objs = [TagCreate.model_validate(obj) for obj in tags_data]
    await db.tags.bulk_create(tags_objs)
    await db.commit()

@pytest.fixture(autouse=True)
async def recipe_creation_fixture(
):
    initial_data = {
        "name": "name",
        "text": "text",
        "cooking_time": 10,
        "tags": [
            2,
            3
        ],
        "ingredients": [
            {
                "id": 1,
                "amount": 100
            },
            {
                "id": 2,
                "amount": 200
            }
        ],
        "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg=="
    }
    recipe_data = RecipeCreateRequest(
        name=initial_data['name'],
        text=initial_data['text'],
        cooking_time=initial_data['cooking_time'],
        tags=initial_data['tags'],
        ingredients=initial_data['ingredients'],
        image=initial_data['image']
    )
    return recipe_data

@pytest.fixture()
async def recipe_updating_fixture(
):
    initial_data = {
        "name": "updated name",
        "text": "updated text",
        "cooking_time": 20,
        "tags": [
            4,
        ],
        "ingredients": [
            {
                "id": 3,
                "amount": 300
            },
            {
                "id": 3,
                "amount": 400
            }
        ],
        "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEBAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg=="
    }
    recipe_data = RecipeUpdateRequest(
        name=initial_data['name'],
        text=initial_data['text'],
        cooking_time=initial_data['cooking_time'],
        tags=initial_data['tags'],
        ingredients=initial_data['ingredients'],
        image=initial_data['image']
    )
    return recipe_data
