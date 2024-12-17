import json
import os
import pathlib
from unittest import mock


def disable_cache(*args, **kwargs):
    def wrapper(func):
        return func

    return wrapper


mock.patch('fastapi_cache.decorator.cache', disable_cache).start()

import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select, delete

from backend.src.base import *
from backend.src.config import settings
from backend.src.constants import MOUNT_PATH
from backend.src.db import engine, async_session_maker
from backend.src.db_manager import DBManager
from backend.src.main import app
from backend.src.models.recipes import ImageModel
from backend.src.schemas.ingredients import IngredientCreate
from backend.src.schemas.recipes import RecipeCreateRequest, RecipeUpdateRequest, ShoppingCartRecipeCreate, \
    FavoriteRecipeCreate
from backend.src.schemas.tags import TagCreate
from backend.src.repositories.utils.users import decode_token


MAX_EMAIL_LENGTH = 254
USER_PARAMS_MAX_LENGTH = 150
PARAMS_MAX_LENGTH = 200


def pytest_configure():
    return {'recipe': None}


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
        for image in image_list:
            image_to_delete = (
                f'{media_path}/src{MOUNT_PATH}/{image}'
            )
            # print(image_to_delete)
            if os.path.exists(image_to_delete):
                os.remove(image_to_delete)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    with open('tests/mock_ingredients.json', 'r') as file:
        ingredients = json.load(file)
    ingredients_data = [IngredientCreate.model_validate(obj_data) for obj_data in ingredients]

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

    async with DBManager(session_factory=async_session_maker) as _db:
        await _db.ingredients.bulk_create(ingredients_data)
        await _db.commit()

        await _db.tags.bulk_create(tags_objs)
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
        json={
            "email": "test_user_1@ya.net",
            "password": "string",
            "username": "test_user_1",
        })
    assert new_user.status_code == status.HTTP_201_CREATED
    another_new_user = await ac.post(
        "/api/users",
        json={
            "email": "test_user_2@ya.net",
            "password": "string",
            "username": "test_user_2",
        })
    assert another_new_user.status_code == status.HTTP_201_CREATED


@pytest.fixture(scope='session')
async def auth_ac(ac):
    jwt_token = await ac.post(
        'api/auth/token/login',
        json={
            "email": "test_user_1@ya.net",
            "password": "string"
        }
    )
    assert jwt_token.status_code == status.HTTP_201_CREATED
    assert isinstance(jwt_token.json()['auth_token'], str)
    # return ac
    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            headers={'Authorization': f'Token {jwt_token.json()["auth_token"]}'}) as ac:
        yield ac


@pytest.fixture(scope='session')
async def another_auth_ac(ac):
    jwt_token = await ac.post(
        'api/auth/token/login',
        json={
            "email": "test_user_2@ya.net",
            "password": "string"
        }
    )
    assert jwt_token.status_code == status.HTTP_201_CREATED, 'Статус успешного создания токена должен быть 201'
    assert isinstance(jwt_token.json()['auth_token'], str)
    # return ac
    print(jwt_token.json())
    # print(decode_token(jwt_token.json()))
    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            headers={'Authorization': f'Token {jwt_token.json()["auth_token"]}'}) as ac:
        yield ac


@pytest.fixture()
async def recipe_creation_fixture():
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
        "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1"
                 "/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg=="
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
async def recipe_updating_fixture():
    initial_data = {
        "name": "updated name",
        "text": "updated text",
        "cooking_time": 20,
        "tags": [
            1,
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
        "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEBAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1"
                 "/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg=="
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


@pytest.fixture()
async def recipe_bulk_creating_fixture(db, recipe_creation_fixture):
    tags_combinations = ([1], [2], [3], [1, 2], [1, 3], [2, 3], [1, 2, 3])
    recipe_author_ids = (1, 1, 1, 2, 2, 2, 2)
    recipe_ids = list()
    for _ in range(len(tags_combinations)):
        current_recipe = recipe_creation_fixture
        current_recipe.tags = tags_combinations[_]
        recipe = await db.recipes.create(recipe_data=current_recipe, db=db, current_user_id=recipe_author_ids[_])
        if recipe.id % 2 == 1:
            shopping_cart_creation_data = ShoppingCartRecipeCreate(
                recipe_id=recipe.id,
                user_id=2
            )
            await db.shopping_cart.create(data=shopping_cart_creation_data)
            favorite_recipe_data = FavoriteRecipeCreate(
                recipe_id=recipe.id,
                user_id=1
            )
            await db.favorite_recipes.create(data=favorite_recipe_data)
        else:
            shopping_cart_creation_data = ShoppingCartRecipeCreate(
                recipe_id=recipe.id,
                user_id=1
            )
            await db.shopping_cart.create(data=shopping_cart_creation_data)
            favorite_recipe_data = FavoriteRecipeCreate(
                recipe_id=recipe.id,
                user_id=2
            )
            await db.favorite_recipes.create(data=favorite_recipe_data)

    recipes_data = {
        'author':
            {
                1: 3,
                2: 4
            },
        'tags':
            {
                1: 4,
                2: 4,
                3: 4
            },
        'recipes_count': len(tags_combinations)
    }
    await db.commit()
    return {'result': recipes_data}


@pytest.fixture()
async def removing_recipes_after_tests(db):
    stmt = delete(RecipeModel)
    await db.session.execute(stmt)
    await db.commit()
    existing_recipes_stmt = select(RecipeModel)
    existing_recipes = await db.session.execute(existing_recipes_stmt)
    return existing_recipes.scalars().all()


@pytest.fixture()
async def removing_recipe_after_test(db, recipe_id):
    stmt = delete(RecipeModel).filter_by(id=recipe_id)
    await db.session.execute(stmt)
    await db.commit()
    existing_recipes_stmt = select(RecipeModel)
    existing_recipes = await db.session.execute(existing_recipes_stmt)
    return existing_recipes.scalars().one()


@pytest.fixture()
async def test_recipe(
        db,
        recipe_creation_fixture: RecipeCreateRequest):
    recipe = await db.recipes.create(
        recipe_data=recipe_creation_fixture,
        db=db,
        current_user_id=1
    )
    await db.commit()
    return recipe


@pytest.fixture()
async def test_recipe_with_all_params(
        db,
        test_recipe
):
    shopping_cart_creation_data = ShoppingCartRecipeCreate(
        recipe_id=test_recipe.id,
        user_id=1
    )
    await db.shopping_cart.create(data=shopping_cart_creation_data)
    favorite_recipe_data = FavoriteRecipeCreate(
        recipe_id=test_recipe.id,
        user_id=1
    )
    await db.favorite_recipes.create(data=favorite_recipe_data)
    await db.commit()
    return test_recipe


@pytest.fixture()
async def test_base64_fixture():
    test_base64_string = ("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEBAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1"
                          "/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==")
    return test_base64_string
