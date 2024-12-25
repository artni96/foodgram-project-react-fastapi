from fastapi import APIRouter, Body, Depends, status, HTTPException

from backend.src.api.dependencies import DBDep
from backend.src.api.dependencies import get_current_superuser
from backend.src.exceptions.base import ObjectNotFoundException
from backend.src.schemas.ingredients import IngredientCreate, IngredientRead
from backend.src.schemas.tags import TagCreate, TagRead
from backend.src.services.only_for_admins import OnlyForAdminService

router = APIRouter(
    prefix="/api/only-for-admins",
    tags=["Для админов"],
    dependencies=[Depends(get_current_superuser)],
)


@router.post(
    "/tags", summary="Создание нового тега", status_code=status.HTTP_201_CREATED
)
async def create_tag(
    db: DBDep,
    data: TagCreate = Body(
        openapi_examples=TagCreate.model_config["json_schema_extra"]
    ),
) -> TagRead:
    return await OnlyForAdminService(db).create_tag(data=data)


@router.post(
    "/ingredients",
    summary="Создание нового ингредиента",
    status_code=status.HTTP_201_CREATED,
)
async def create_ingredient(db: DBDep, data: IngredientCreate) -> IngredientRead:
    return await OnlyForAdminService(db).create_ingredient(data=data)


@router.delete(
    "/tags/{id}", summary="Удаление тега", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_tag(db: DBDep, id: int) -> None:
    try:
        await OnlyForAdminService(db).delete_tag(id=id)
    except ObjectNotFoundException as ex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ex.detail)


@router.delete(
    "/ingredients/{id}",
    summary="Удаление ингредиента",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_ingredient(db: DBDep, id: int) -> None:
    try:
        await OnlyForAdminService(db).delete_ingredient(id=id)
    except ObjectNotFoundException as ex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ex.detail)
