from http import HTTPStatus

from fastapi import APIRouter, Path, Query, status, HTTPException
from loguru import logger
from starlette.requests import Request

from backend.src.api.dependencies import DBDep, UserDep
from backend.src.exceptions.subscriptions import UniqueConstraintSubscriptionException, FollowingYourselfException, \
    SubscriptionNotFoundException
from backend.src.exceptions.users import UserNotFoundException
from backend.src.logging.logs_history.foodgram_logger import api_exception_log, api_success_log
from backend.src.schemas.subscriptions import SubscriptionCreate, SubscriptionListRead
from backend.src.schemas.users import FollowedUserWithRecipiesRead
from backend.src.services.subscriptions import SubscriptionService

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
    request: Request,
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
    response = await SubscriptionService(db).get_my_subscriptions(
        current_user=current_user,
        router_prefix=ROUTER_PREFIX,
        page=page,
        limit=limit,
        recipes_limit=recipes_limit
    )
    logger.info(api_success_log(user=current_user, request=request.url))
    return response


@subscription_router.post(
    '/{user_id}/subscribe',
    status_code=status.HTTP_201_CREATED,
    summary='Подписаться на пользователя',
    description='Доступно только авторизованным пользователям'
)
async def subscribe(
    request: Request,
    db: DBDep,
    current_user: UserDep,
    user_id: int = Path(),
    recipes_limit: int = Query(default=6)
) -> FollowedUserWithRecipiesRead:
    data = SubscriptionCreate(author_id=user_id, subscriber_id=current_user.id)
    try:
        subscription = await db.subscriptions.create(data, recipes_limit)
        await db.commit()
    except FollowingYourselfException as ex:
        logger.warning(api_exception_log(user=current_user, request=request.url, ex=ex))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ex.detail
        )
    except UserNotFoundException as ex:
        logger.warning(api_exception_log(user=current_user, request=request.url, ex=ex))
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=ex.detail
        )
    except UniqueConstraintSubscriptionException as ex:
        logger.warning(api_exception_log(user=current_user, request=request.url, ex=ex))
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=ex.detail
        )
    logger.info(f'Пользователь {current_user.email} успешно подписался на пользователя {subscription.email}')
    return subscription

@subscription_router.delete(
    '/{user_id}/subscribe',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Отписаться от пользователя',
    description='Доступно только авторизованным пользователям'
)
async def unsubscribe(
    request: Request,
    user_id: int,
    db: DBDep,
    current_user: UserDep
) -> None:
    try:
        await SubscriptionService(db).unsubscribe(user_id=user_id, current_user=current_user)
    except SubscriptionNotFoundException as ex:
        logger.warning(api_exception_log(user=current_user, request=request.url, ex=ex))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ex.detail
        )
    except Exception:
        ex = 'Не удалось отменить подписку'
        logger.warning(api_exception_log(user=current_user, request=request.url, ex=ex))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ex
        )
    logger.info(f'Пользователь {current_user.email} успешно подписался на пользователя с id {user_id}')
