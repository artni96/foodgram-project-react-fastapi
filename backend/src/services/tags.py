from backend.src.schemas.tags import TagRead
from backend.src.services.base import BaseService


class TagService(BaseService):
    async def get_tag(
        self,
        id: int
    ) -> TagRead | None:
        result = await self.db.tags.get_one_or_none(id=id)
        return result

    async def get_tags(
        self,
    ) -> list[TagRead] | None:
        result = await self.db.tags.get_all()
        return result
