from fastapi import APIRouter, Body, Depends, status, HTTPException

from backend.src.api.dependencies import DBDep
from backend.src.schemas.ingredients import IngredientCreate, IngredientRead
from backend.src.schemas.tags import TagCreate, TagRead
from backend.src.services.users import current_superuser


router = APIRouter(
    prefix='/api/only-for-admins',
    tags=['Для админов'], dependencies=[Depends(current_superuser)])


@router.post(
    '/tags',
    response_model=TagRead,
    summary='Создание нового тега',
    status_code=status.HTTP_201_CREATED
)
async def create_tag(
    db: DBDep,
    data: TagCreate = Body(
        openapi_examples=TagCreate.model_config['json_schema_extra']
    )
):
    result = await db.tags.create(data=data)
    await db.commit()
    return result


@router.post(
    '/ingredients',
    response_model=IngredientRead,
    summary='Создание нового ингредиента',
    status_code=status.HTTP_201_CREATED
)
async def create_ingredient(
    db: DBDep,
    data: IngredientCreate
):
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
