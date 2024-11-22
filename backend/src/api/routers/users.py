from fastapi import APIRouter, Query, status, Depends, HTTPException

from backend.src import constants
from backend.src.api.dependencies import DBDep, UserDep
from backend.src.repositories.utils.users import PasswordManager
from backend.src.schemas.users import (UserCreate, UserCreateRequest,
                                       UserPasswordChangeRequest,
                                       UserPasswordUpdate)
from backend.src.services.users import auth_backend, fastapi_users, optional_current_user

ROUTER_PREFIX = '/api/users'
user_router = APIRouter(prefix=ROUTER_PREFIX, tags=['Пользователи',])

user_router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix='/token',
)


@user_router.get(
    '',
    status_code=status.HTTP_200_OK,
    summary='Список пользователей',
)
async def get_user_list(
    db: DBDep,
    current_user=Depends(optional_current_user),
    page: int | None = Query(default=None, title='Номер страницы'),
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
    filter_params = {
        'limit': limit,
        'offset': offset,
        'page': page,
        'router_prefix': ROUTER_PREFIX,
        'user_id': None
    }
    if current_user:
        current_user_id = current_user.id
    else:
        current_user_id = None
    result = await db.users.get_all(
        # **filter_params
        user_id=current_user_id,
        limit=limit,
        offset=offset,
        page=page,
        router_prefix=ROUTER_PREFIX
    )
    return result


@user_router.get(
    '/me',
    status_code=status.HTTP_200_OK,
    summary='Текущий пользователь'
)
async def get_current_user(
    db: DBDep,
    current_user: UserDep
):
    current_user = await db.users.get_one_or_none(
        user_id=current_user.id)
    return current_user


@user_router.get(
    '/{id}',
    status_code=status.HTTP_200_OK,
    summary='Профиль пользователя',
    description='Доступно всем пользователям.'
)
async def get_user_by_id(
    db: DBDep,
    id: int,
    current_user=Depends(optional_current_user)
):
    options = {}
    if current_user:
        options['current_user_id'] = current_user.id
    user_to_get = await db.users.get_one_or_none(
        user_id=id,
        **options
    )
    return user_to_get


@user_router.post(
    '',
    status_code=status.HTTP_201_CREATED,
    summary='Регистрация пользователя'
)
async def create_new_user(
    db: DBDep,
    user_data: UserCreateRequest
):
    hashed_password = PasswordManager().hash_password(user_data.password)
    _user_data = UserCreate(
        username=user_data.username,
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        hashed_password=hashed_password
    )
    new_user = await db.users.create(data=_user_data)
    await db.commit()
    return new_user


@user_router.post(
    '/set_password',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Изменение пароля',
    description='Изменение пароля текущего пользователя'
)
async def change_password(
    db: DBDep,
    password_data: UserPasswordUpdate,
    current_user: UserDep
):
    user = await db.users.get_user_hashed_password(current_user.id)
    try:
        PasswordManager().verify_password(
            user.hashed_password,
            password_data.current_password
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Неверный пароль'
    )
    new_hashed_password = PasswordManager().hash_password(
        password_data.new_password
    )
    password_updated_data = UserPasswordChangeRequest(
        hashed_password=new_hashed_password
    )
    await db.users.update(
        id=current_user.id,
        data=password_updated_data,
        exclude_unset=True
    )
    await db.commit()


route_desired_content = [
    [
        "auth:jwt.login",
        "Используется для авторизации по емейлу и паролю, чтобы далее "
        "использовать токен при запросах",
        "Получить токен авторизации"
    ],
    [
        "auth:jwt.logout",
        "Удаляет токен текущего пользователя",
        "Удаление токена"
    ]
]

for x in range(0, len(route_desired_content)):
    route_name = user_router.routes[x].name
    for z in route_desired_content:
        if route_name == z[0]:
            user_router.routes[x].description = z[1]
            user_router.routes[x].name = z[2]
