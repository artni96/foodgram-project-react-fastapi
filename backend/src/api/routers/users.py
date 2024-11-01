from fastapi import APIRouter, status
from passlib.context import CryptContext
from sqlalchemy import select

from backend.src.api.dependencies import DBDep, UserDep
from backend.src.db import async_session_maker
from backend.src.models.users import UserModel
from backend.src.schemas.users import (BaseUserRead,
                                       UserCreate, UserCreateRequest)
from backend.src.services.users import auth_backend, fastapi_users


user_router = APIRouter(prefix='/api/users', tags=['Пользователи',])


user_router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix='/token',
)


@user_router.get('/')
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
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = pwd_context.hash(user_data.password)
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
