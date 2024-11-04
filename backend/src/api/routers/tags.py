from fastapi import APIRouter, status

from backend.src.api.dependencies import DBDep
from backend.src.schemas.tags import TagRead


router = APIRouter(prefix='/tags', tags=['Теги',])


@router.get(
    '/{id}',
    status_code=status.HTTP_200_OK,
    summary='Получение тега'
)
async def get_tag(
    id: int,
    db: DBDep
) -> TagRead | None:
    result = await db.tags.get_one_or_none(id=id)
    return result


@router.get(
    '/',
    status_code=status.HTTP_200_OK,
    summary='Cписок тегов'
)
async def get_tags(
    db: DBDep
) -> list[TagRead]:
    result = await db.tags.get_all()
    return result
