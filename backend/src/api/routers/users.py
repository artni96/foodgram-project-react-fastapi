from fastapi import APIRouter, status
from sqlalchemy import select

from backend.src.api.dependencies import DBDep, UserDep
from backend.src.db import async_session_maker
from backend.src.models.users import UserModel
from backend.src.repositories.utils.users import PasswordManager
from backend.src.schemas.users import (BaseUserRead, UserCreate,
                                       UserCreateRequest,
                                       UserPasswordChangeRequest,
                                       UserPasswordUpdate)
from backend.src.services.users import auth_backend, fastapi_users


user_router = APIRouter(prefix='/api/users', tags=['Пользователи',])


user_router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix='/token',
)


@user_router.get(
    '/',
    status_code=status.HTTP_200_OK,
    summary='Список пользователей',
)
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


@user_router.get(
    '/me',
    status_code=status.HTTP_200_OK
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
    status_code=status.HTTP_200_OK
)
async def get_user_by_id(
    db: DBDep,
    id: int,
    current_user: UserDep
):
    user_to_get = await db.users.get_one_or_none(
        user_id=id,
        current_user_id=current_user.id)
    return user_to_get


@user_router.post(
    '/',
    status_code=status.HTTP_201_CREATED
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
    status_code=status.HTTP_204_NO_CONTENT
)
async def change_password(
    db: DBDep,
    password_data: UserPasswordUpdate,
    current_user: UserDep
):
    user = await db.users.get_user_hashed_password(current_user.id)
    if PasswordManager().verify_password(user.hashed_password, password_data.current_password):
        new_hashed_password = ph.hash(password_data.new_password)
        password_updated_data = UserPasswordChangeRequest(
            hashed_password=new_hashed_password
        )
        await db.users.update(
            id=current_user.id,
            data=password_updated_data,
            exclude_unset=True
        )
        await db.commit()
