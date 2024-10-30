from fastapi import APIRouter

from backend.src.schemas.users import UserCreate, UserRead, UserUpdate
from backend.src.services.users import auth_backend, fastapi_users
from sqlalchemy import select
from backend.src.models.users import UserModel
from backend.src.db import async_session_maker
from backend.src.schemas.users import UserRead, BaseUserRead, SubscriptionCreate
from backend.src.api.dependencies import UserDep, DPDep
from fastapi import Path

user_router = APIRouter()


user_router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix='/auth/jwt',
    # tags=['Авторизация и аутентификация'],
)
user_router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix='/users',
    tags=['Авторизация и аутентификация'],
)
users_router = fastapi_users.get_users_router(UserRead, UserUpdate)
print(users_router.routes)

users_router.routes = [
    rout for rout in users_router.routes if (
        rout.name != 'users:delete_user' or
        rout.name != 'users:'
    )
]  # удаление ручки для удаления пользователя

user_router.include_router(
    users_router,
    prefix='/users',
    tags=['Пользователи'],
)


@user_router.get('/test123')
async def get_user_list():

    async with async_session_maker() as session:
        query = select(
            UserModel.id,
            UserModel.username,
            UserModel.email,
            UserModel.first_name,
            UserModel.last_name
        )
        result = await session.execute(query)
        return [BaseUserRead.model_validate(obj, from_attributes=True)
                for obj in result.mappings().all()]


@user_router.post('/{user_id}/subscribe')
async def to_subsrtibe(
    db: DPDep,
    current_user: UserDep,
    user_id: int = Path()
):
    data = SubscriptionCreate(author_id=user_id, subscriber_id=current_user.id)
    subscription = await db.subscriptions.create(data)
    result = await db.users.get_one_or_none(id=subscription)
    return result
