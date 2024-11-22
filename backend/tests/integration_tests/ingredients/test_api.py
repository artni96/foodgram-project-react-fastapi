from fastapi import status
from backend.src.config import settings

async def test_get_ingredient_by_id(check_test_mode, auth_ac):
    ingredient_id = 1
    ingredient = await auth_ac.get(
        f'api/ingredients/{ingredient_id}'
    )
    assert ingredient.status_code == status.HTTP_200_OK
    not_existant_ingredient = await auth_ac.get(
        f'api/ingredients/11'
    )
    assert not_existant_ingredient.json() is None


async def test_get_ingredient_list(check_test_mode, auth_ac):
    ingredient_list = await auth_ac.get(
        'api/ingredients'
    )
    assert ingredient_list.status_code == status.HTTP_200_OK
    assert len(ingredient_list.json()) == 10


async def test_get_filtered_ingredients_by_name(check_test_mode, auth_ac):
    ingredient_list = await auth_ac.get(
        'api/ingredients',
        params={'name': 'абрикосы'}
    )
    # print(ingredient_list.json())
    assert len(ingredient_list.json()) == 2
    assert 'id' in ingredient_list.json()[0]
    assert 'name' in ingredient_list.json()[0]
    assert 'measurement_unit' in ingredient_list.json()[0]
    assert ingredient_list.status_code == status.HTTP_200_OK