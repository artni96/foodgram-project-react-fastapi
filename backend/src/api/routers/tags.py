from fastapi import APIRouter, status
from fastapi_cache.decorator import cache

from backend.src.api.dependencies import DBDep
from backend.src.schemas.tags import TagRead
from backend.src.services.tags import TagService

router = APIRouter(prefix='/api/tags', tags=['Теги',])


@router.get(
    '/{id}',
    status_code=status.HTTP_200_OK,
    summary='Получение тега'
)
@cache(expire=60)
async def get_tag(
    id: int,
    db: DBDep
) -> TagRead | None:
    return await TagService(db).get_tag(id=id)


@router.get(
    '',
    status_code=status.HTTP_200_OK,
    summary='Cписок тегов'
)
@cache(expire=60)
async def get_tags(
    db: DBDep
) -> list[TagRead] | None:
    return await TagService(db).get_tags()
