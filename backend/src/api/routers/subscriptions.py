from fastapi import APIRouter, Path, Query, status

from backend.src import constants
from backend.src.api.dependencies import DBDep, UserDep
from backend.src.schemas.subscriptions import SubscriptionCreate
from backend.src.schemas.users import UserRead


subscription_router = APIRouter(tags=['Подписки'], prefix='/api/users')


@subscription_router.get(
    '/subscriptions',
    status_code=status.HTTP_200_OK,
    summary='Мои подписки',
    description=(
        'Возвращает пользователей, на которых подписан текущий пользователь. '
        'В выдачу добавляются рецепты.'
    )
)
async def get_my_subscriptions(
    db: DBDep,
    current_user: UserDep,
    page: int | None = Query(
        default=None,
        title='Номер страницы'
    ),
    limit: int | None = Query(
        default=None,
        title='Количество объектов на странице'
    )
):
    if not limit:
        limit = constants.PAGINATION_LIMIT
    if page:
        offset = (page - 1) * limit
    else:
        offset = None
    user_subs = await db.subscriptions.get_user_subs(
        user_id=current_user.id,
        limit=limit,
        offset=offset,
        page=page
    )
    return user_subs


@subscription_router.post(
    '/{user_id}/subscribe',
    status_code=status.HTTP_201_CREATED,
    summary='Подписаться на пользователя',
    description='Доступно только авторизованным пользователям'
)
async def subsrtibe(
    db: DBDep,
    current_user: UserDep,
    user_id: int = Path()
) -> UserRead:
    data = SubscriptionCreate(author_id=user_id, subscriber_id=current_user.id)
    subscription = await db.subscriptions.create(data)
    await db.commit()
    return subscription


@subscription_router.delete(
    '/{user_id}/subscribe',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Отписаться от пользователя',
    description='Доступно только авторизованным пользователям'
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
