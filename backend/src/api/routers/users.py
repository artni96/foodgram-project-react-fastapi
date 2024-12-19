from fastapi import APIRouter, Query, status, HTTPException, Response
from fastapi_cache.decorator import cache
from starlette.status import HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST

from backend.src.api.dependencies import DBDep, UserDep, OptionalUserDep
from backend.src.exceptions.users import IncorrectPasswordException, \
    IncorrectTokenException, UserNotFoundException
from backend.src.schemas.users import (UserCreateRequest,
                                       UserPasswordUpdate, UserListRead, UserCreateResponse, FollowedUserRead,
                                       UserLoginRequest)
from backend.src.services.users import UserService

ROUTER_PREFIX = '/api/users'
user_router = APIRouter(prefix=ROUTER_PREFIX, tags=['Пользователи',])
auth_router = APIRouter(prefix='/api/auth', tags=['Пользователи',])


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
    return await UserService(db).get_user_list(
        current_user=current_user,
        router_prefix=ROUTER_PREFIX,
        page=page,
        limit=limit
)


@user_router.get(
    '/me',
    status_code=status.HTTP_200_OK,
    summary='Текущий пользователь'
)
async def get_current_user(
    db: DBDep,
    current_user: UserDep
) -> FollowedUserRead | None:
    return await UserService(db).get_current_user(current_user=current_user)

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
    try:
        return await UserService(db).get_user_by_id(id=id, options=options)
    except UserNotFoundException as ex:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=ex.detail)


@user_router.post(
    '',
    status_code=status.HTTP_201_CREATED,
    summary='Регистрация пользователя'
)
async def create_new_user(
    db: DBDep,
    user_data: UserCreateRequest
) -> UserCreateResponse:
    return await UserService(db).create_new_user(user_data=user_data)


@auth_router.post(
    "/token/login",
    summary='Вход пользователя в систему',
    status_code=status.HTTP_201_CREATED
)
async def login_user(
    data: UserLoginRequest,
    db: DBDep,
):
    try:
        access_token = await UserService(db).login_user(data=data)
    except UserNotFoundException as ex:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ex.detail)
    except IncorrectPasswordException as ex:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ex.detail)
    return {"auth_token": access_token}


@auth_router.post(
    "/token/logout",
    summary='Выход пользователя из системы',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(response: Response, user: UserDep):
    try:
        response.delete_cookie("auth_token")
    except IncorrectTokenException as ex:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ex.detail)


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
    try:
        await UserService(db).change_password(password_data=password_data, current_user=current_user)
    except IncorrectPasswordException as ex:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=ex.detail)
