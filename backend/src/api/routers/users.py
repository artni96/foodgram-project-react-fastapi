from fastapi import APIRouter, Query, status, Depends, HTTPException, Response, Request
from fastapi_cache.decorator import cache

from backend.src import constants
from backend.src.api.dependencies import DBDep, UserDep, OptionalUserDep
from backend.src.exceptions.users import EmailNotRegisteredException, IncorrectPasswordException, \
    IncorrectTokenException
from backend.src.repositories.utils.users import PasswordManager
from backend.src.schemas.users import (UserCreate, UserCreateRequest,
                                       UserPasswordChangeRequest,
                                       UserPasswordUpdate, UserListRead, UserCreateResponse, FollowedUserRead,
                                       UserLoginRequest)
# from backend.src.services.users import auth_backend, fastapi_users, optional_current_user

ROUTER_PREFIX = '/api/users'
user_router = APIRouter(prefix=ROUTER_PREFIX, tags=['Пользователи',])
auth_router = APIRouter(prefix='/api/auth', tags=['Пользователи',])

# auth_router.include_router(
#     fastapi_users.get_auth_router(auth_backend),
#     prefix='/token',
# )


@user_router.get(
    '',
    status_code=status.HTTP_200_OK,
    summary='Список пользователей',
)
@cache(expire=60)
async def get_user_list(
    db: DBDep,
    current_user=OptionalUserDep,
    page: int | None = Query(default=None, title='Номер страницы'),
    limit: int | None = Query(
        default=None,
        title='Количество объектов на странице'
    )
) -> UserListRead:
    if not limit:
        limit = constants.PAGINATION_LIMIT
    if page:
        offset = (page - 1) * limit
    else:
        offset = None

    if current_user:
        current_user_id = current_user.id
    else:
        current_user_id = None
    result = await db.users.get_all(
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
) -> FollowedUserRead | None:
    current_user = await db.users.get_one_or_none(user_id=current_user.id)
    return current_user


@user_router.get(
    '/{id}',
    status_code=status.HTTP_200_OK,
    summary='Профиль пользователя',
    description='Доступно всем пользователям.'
)
@cache(expire=60)
async def get_user_by_id(
    db: DBDep,
    id: int,
    current_user=OptionalUserDep
) -> FollowedUserRead | None:
    options = {}
    if current_user:
        options['current_user_id'] = current_user.id
    user_to_get = await db.users.get_one_or_none(
        user_id=id,
        **options
    )
    if not user_to_get:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Пользователь не найден.'
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
) -> UserCreateResponse:
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


@auth_router.post(
    "/token/login",
    summary='Вход пользователя в систему',
    status_code=status.HTTP_201_CREATED
)
async def login_user(
    data: UserLoginRequest,
    response: Response,
    db: DBDep,
):
    try:
        # access_token = await AuthService(db).login_user(data)
        access_token = await db.users.create_access_token(data=data)
    except EmailNotRegisteredException as ex:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ex.detail)
    except IncorrectPasswordException as ex:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ex.detail)

    response.set_cookie("access_token", access_token)
    return {"access_token": access_token}


@auth_router.post(
    "/token/logout",
    summary='Выход пользователя из системы',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(response: Response, user: UserDep):
    try:
        response.delete_cookie("access_token")
    except IncorrectTokenException as ex:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ex.detail)
    return {"status": "OK"}


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
) -> None:
    user = await db.users.get_user_hashed_password(id=current_user.id)
    if not PasswordManager().verify_password(
            hashed_password=user.hashed_password,
            plain_password=password_data.current_password
        ):
        # except Exception:
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
