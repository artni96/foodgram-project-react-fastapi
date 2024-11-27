from fastapi import status
from backend.src.config import settings

async def test_get_ingredient_by_id(check_test_mode, auth_ac):
    ingredient_id = 1
    ingredient = await auth_ac.get(
        f'api/ingredients/{ingredient_id}'
    )
    assert ingredient.status_code == status.HTTP_200_OK, 'статус ответа отличается от 200'
    not_existent_ingredient = await auth_ac.get(
        f'api/ingredients/11'
    )
    assert not not_existent_ingredient.json()


async def test_get_ingredient_list(check_test_mode, auth_ac):
    ingredient_list = await auth_ac.get(
        'api/ingredients'
    )
    assert ingredient_list.status_code == status.HTTP_200_OK, 'статус ответа отличается от 200'
    assert len(ingredient_list.json()) == 10, 'неверное количество ингредиентов в ответе'


async def test_get_filtered_ingredients_by_name(check_test_mode, auth_ac):
    ingredient_list = await auth_ac.get(
        'api/ingredients',
        params={'name': 'абрикосы'}
    )
    assert ingredient_list.status_code == status.HTTP_200_OK, 'статус ответа отличается от 200'
    assert len(ingredient_list.json()) == 2, 'неверное количество ингредиентов в ответе, проблемы с фильтрацией'
    assert 'id' in ingredient_list.json()[0], 'в ответе отсутствует поле id'
    assert 'name' in ingredient_list.json()[0], 'в ответе отсутствует поле name'
    assert 'measurement_unit' in ingredient_list.json()[0], 'в ответе отсутствует поле measurement_unit'
