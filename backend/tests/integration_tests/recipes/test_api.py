import pytest
from fastapi import status
from starlette.status import HTTP_404_NOT_FOUND


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
                [1, 5],
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
                status.HTTP_404_NOT_FOUND
        )
    ]
)
async def test_recipe_flow_by_auth(
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
    if new_recipe.status_code == HTTP_404_NOT_FOUND:
        print(new_recipe.json()['detail'])