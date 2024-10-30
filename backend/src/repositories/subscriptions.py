from backend.src.repositories.base import BaseRepository
from backend.src.models.users import SubscriptionModel
from backend.src.schemas.users import BaseUserRead, SubscriptionCreate
from sqlalchemy import insert


class SubscriptionRepository(BaseRepository):

    model = SubscriptionModel
    schema = BaseUserRead

    async def create(self, data: SubscriptionCreate):
        subscription_stmt = (
            insert(self.model)
            .values(**data.model_dump())
            .returning(self.model.author_id)
        )
        result = await self.session.execute(subscription_stmt)
        await self.session.commit()
        return result.scalars().one()
