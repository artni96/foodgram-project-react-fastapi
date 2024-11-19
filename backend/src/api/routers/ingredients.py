from fastapi import APIRouter, status

from backend.src.api.dependencies import DBDep


router = APIRouter(prefix='/api/ingredients', tags=['Ингредиенты'])


@router.get(
    '/{id}',
    summary='Получение ингредиента',
    description='Уникальный идентификатор этого ингредиента.',
    status_code=status.HTTP_200_OK
)
async def get_ingredient_by_id(
    db: DBDep,
    id: int
):
    result = await db.ingredients.get_one_or_none(id=id)
    return result


@router.get(
    '',
    summary='Список ингредиентов',
    description='Список ингредиентов с возможностью поиска по имени.',
    status_code=status.HTTP_200_OK
)
async def get_filtered_ingredients_by_name(
    db: DBDep,
    name: str | None = None
):
    result = await db.ingredients.get_filtered(name=name)
    return result
