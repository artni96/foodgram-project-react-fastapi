from backend.src import constants
from backend.src.schemas.subscriptions import SubscriptionListRead, SubscriptionCreate
from backend.src.schemas.users import FollowedUserWithRecipiesRead
from backend.src.services.base import BaseService


class SubscriptionService(BaseService):
    async def get_my_subscriptions(
        self,
        current_user,
        router_prefix,
        page: int | None = None,
        limit: int | None = None,
        recipes_limit: int | None = None,
    ) -> SubscriptionListRead | None:
        if not limit:
            limit = constants.PAGINATION_LIMIT
        if page:
            offset = (page - 1) * limit
        else:
            offset = None
        user_subs = await self.db.subscriptions.get_user_subs(
            user_id=current_user.id,
            limit=limit,
            offset=offset,
            page=page,
            router_prefix=f'{router_prefix}/subscriptions',
            recipes_limit=recipes_limit
        )
        return user_subs

    async def subscribe(
        self,
        current_user,
        user_id: int,
        recipes_limit: int,
    ) -> FollowedUserWithRecipiesRead:
        data = SubscriptionCreate(author_id=user_id, subscriber_id=current_user.id)
        subscription = await self.db.subscriptions.create(data, recipes_limit)
        await self.db.commit()
        return subscription

    async def unsubscribe(
        self,
        user_id: int,
        current_user
    ) -> None:
        await self.db.subscriptions.delete(
            author_id=user_id,
            subscriber_id=current_user.id
        )
        await self.db.commit()
