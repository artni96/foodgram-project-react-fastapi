from fastapi import APIRouter, Body, Depends, status

from backend.src.api.dependencies import DBDep
from backend.src.schemas.ingredients import IngredientCreate, IngredientRead
from backend.src.schemas.tags import TagCreate, TagRead
from backend.src.api.dependencies import get_current_superuser


router = APIRouter(
    prefix='/api/only-for-admins',
    tags=['Для админов'], dependencies=[Depends(get_current_superuser)])


@router.post(
    '/tags',
    summary='Создание нового тега',
    status_code=status.HTTP_201_CREATED
)
async def create_tag(
        db: DBDep,
        data: TagCreate = Body(
            openapi_examples=TagCreate.model_config['json_schema_extra']
        )
) -> TagRead:
    result = await db.tags.create(data=data)
    await db.commit()
    return result


@router.post(
    '/ingredients',
    summary='Создание нового ингредиента',
    status_code=status.HTTP_201_CREATED
)
async def create_ingredient(
        db: DBDep,
        data: IngredientCreate
) -> IngredientRead:
    result = await db.ingredients.create(data=data)
    await db.commit()
    return result


@router.delete(
    '/tags/{id}',
    summary='Удаление тега',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_tag(
        db: DBDep,
        id: int
) -> None:
    await db.tags.delete(id=id)
    await db.commit()


@router.delete(
    '/ingredients/{id}',
    summary='Удаление ингредиента',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_ingredient(
        db: DBDep,
        id: int
) -> None:
    await db.ingredients.delete(id=id)
    await db.commit()
