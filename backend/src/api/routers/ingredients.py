from fastapi import APIRouter, status

from backend.src.api.dependencies import DBDep

router = APIRouter(prefix='/api/ingredients', tags=['Ингредиенты'])


@router.get(
    '/{id}',
    summary='Поиск по частичному вхождению в начале названия ингредиента.',
    status_code=status.HTTP_200_OK
)
async def get_ingredient_by_id(
    db: DBDep,
    id: int
):
    result = await db.ingredients.get_one_or_none(id=id)
    return result
