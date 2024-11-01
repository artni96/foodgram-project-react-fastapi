from fastapi import APIRouter, Path, status

from backend.src.api.dependencies import DBDep, UserDep
from backend.src.schemas.users import BaseUserRead
from backend.src.schemas.subscriptions import SubscriptionCreate

subscription_router = APIRouter(tags=['Подписки'])


@subscription_router.post(
    '/{user_id}/subscribe',
    status_code=status.HTTP_201_CREATED
)
async def subsrtibe(
    db: DBDep,
    current_user: UserDep,
    user_id: int = Path()
) -> BaseUserRead:
    data = SubscriptionCreate(author_id=user_id, subscriber_id=current_user.id)
    subscription = await db.subscriptions.create(data)
    await db.commit()
    return subscription


@subscription_router.delete(
    '/{user_id}/subscribe',
    status_code=status.HTTP_204_NO_CONTENT
)
async def unsubscribe(
    user_id: int,
    db: DBDep,
    current_user: UserDep
) -> None:
    await db.subscriptions.delete(
        author_id=user_id,
        subscriber_id=current_user.id
    )
    await db.commit()
