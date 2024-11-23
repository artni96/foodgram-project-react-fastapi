import pytest
from fastapi import status

from backend.tests.conftest import PARAMS_MAX_LENGTH


@pytest.mark.parametrize(
    'name, text, cooking_time, tags, ingredients, image, status_code',
    [
        (
            'test name',
            'test text',
            10,
            [2, 3],
            [
                {
                    "id": 1,
                    "amount": 100
                },
                {
                    "id": 2,
                    "amount": 200
                }
            ],
            "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
            status.HTTP_201_CREATED
        ),
        (
            'test name',
            'test text',
            10,
            [3, 4],
            [
                {
                    "id": 21,
                    "amount": 100
                },
                {
                    "id": 22,
                    "amount": 200
                }
            ],
            "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
            status.HTTP_400_BAD_REQUEST
        ),
        (
            'test name',
            'test text',
            10,
            [1, 5],
            [
                {
                    "id": 1,
                    "amount": 100
                },
                {
                    "id": 2,
                    "amount": 200
                }
            ],
            "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
            status.HTTP_400_BAD_REQUEST
        ),
        (
            f'{"".join(["t"] * (PARAMS_MAX_LENGTH+1))}',
            'test text',
            10,
            [2, 3],
            [
                {
                    "id": 1,
                    "amount": 100
                },
                {
                    "id": 2,
                    "amount": 200
                }
            ],
            "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
            status.HTTP_400_BAD_REQUEST
        ),
    ]
)
async def test_recipe_creating(
    auth_ac,
    name,
    text,
    cooking_time,
    tags,
    ingredients,
    image,
    status_code
):
    new_recipe = await auth_ac.post(
        '/api/recipes',
        json={
            "name": name,
            "text": text,
            "cooking_time": cooking_time,
            "tags": tags,
            "ingredients": ingredients,
            "image": image
        }
    )
    assert new_recipe.status_code == status_code
    if new_recipe.status_code == status.HTTP_201_CREATED:
        assert new_recipe.json()['name'] == name
        assert new_recipe.json()['text'] == text
        assert new_recipe.json()['cooking_time'] == cooking_time


@pytest.mark.parametrize(
    'name, text, cooking_time, tags, ingredients, image, status_code',
    [
        (
            'updated name',
            'updated text',
            20,
            [4, 4, 4, 4],
            [
                {
                    "id": 5,
                    "amount": 100
                },
                {
                    "id": 5,
                    "amount": 200
                }
            ],
            "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
            status.HTTP_200_OK
        ),
        (
            'updated name',
            'updated text',
            20,
            [1, 2, 3, 4],
            [
                {
                    "id": 6,
                    "amount": 200
                },
                {
                    "id": 6,
                    "amount": 300
                }
            ],
            "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
            status.HTTP_400_BAD_REQUEST
        ),
        (
            f'{"".join(["t"] * (PARAMS_MAX_LENGTH+1))}',
            'updated text',
            20,
            [4, 4, 4, 4],
            [
                {
                    "id": 5,
                    "amount": 100
                },
                {
                    "id": 5,
                    "amount": 200
                }
            ],
            "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
            status.HTTP_400_BAD_REQUEST
        )
    ]
)

async def test_recipe_updating(
    auth_ac,
    name,
    text,
    cooking_time,
    tags,
    ingredients,
    image,
    status_code
):
    recipes = await auth_ac.get(
        '/api/recipes'
    )
    recipe_to_update = recipes.json()['result'][0]['id']
    updated_recipe = await auth_ac.patch(
        f'/api/recipes/{recipe_to_update}',
        json={
            "name": name,
            "text": text,
            "cooking_time": cooking_time,
            "tags": tags,
            "ingredients": ingredients,
            "image": image
        }
    )
    assert updated_recipe.status_code == status_code
    if updated_recipe.status_code == status.HTTP_200_OK:
        assert updated_recipe.json()['name'] == name
        assert updated_recipe.json()['text'] == text
        assert updated_recipe.json()['cooking_time'] == cooking_time


async def test_recipe_removing(auth_ac):
    recipes = await auth_ac.get(
        '/api/recipes'
    )
    recipe_to_delete = recipes.json()['result'][0]['id']
    removed_recipe = await auth_ac.delete(
        f'/api/recipes/{recipe_to_delete}'
    )
    assert removed_recipe.status_code == status.HTTP_204_NO_CONTENT
