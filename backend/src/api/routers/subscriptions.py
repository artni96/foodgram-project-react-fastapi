from http import HTTPStatus

from fastapi import APIRouter, Path, Query, status, HTTPException
from sqlalchemy.exc import NoResultFound, IntegrityError

from backend.src import constants
from backend.src.api.dependencies import DBDep, UserDep
from backend.src.schemas.subscriptions import SubscriptionCreate, SubscriptionListRead
from backend.src.schemas.users import FollowedUserWithRecipiesRead


ROUTER_PREFIX = '/api/users'
subscription_router = APIRouter(tags=['Подписки'], prefix=ROUTER_PREFIX)


@subscription_router.get(
    path='/subscriptions',
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
    ),
    recipes_limit: int | None = Query(
        default=None,
        title='Количество объектов внутри поля recipes.'
    ),
) -> SubscriptionListRead | None:
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
        page=page,
        router_prefix=f'{ROUTER_PREFIX}/subscriptions',
        recipes_limit=recipes_limit
    )
    return user_subs


@subscription_router.post(
    '/{user_id}/subscribe',
    status_code=status.HTTP_201_CREATED,
    summary='Подписаться на пользователя',
    description='Доступно только авторизованным пользователям'
)
async def subscribe(
    db: DBDep,
    current_user: UserDep,
    user_id: int = Path(),
    recipes_limit: int = Query(default=6)
) -> FollowedUserWithRecipiesRead:
    data = SubscriptionCreate(author_id=user_id, subscriber_id=current_user.id)
    try:
        subscription = await db.subscriptions.create(data, recipes_limit)
        await db.commit()
        return subscription

    except IntegrityError as e:
        if 'ForeignKeyViolationError' in str(e.__cause__):
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Пользователь не найден!'
            )
        elif 'UniqueViolationError' in str(e.__cause__):
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Вы уже подписанны на данного пользователя!'
            )


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
    try:
        await db.subscriptions.delete(
            author_id=user_id,
            subscriber_id=current_user.id
        )
        await db.commit()

    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Подписка на пользователя с id {user_id} не найдена.'
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Не удалось отменить подписку.'
        )
