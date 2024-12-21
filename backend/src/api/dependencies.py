from typing import Annotated

from fastapi import Depends, Request, HTTPException
from loguru import logger
from starlette import status

from backend.src.db import async_session_maker
from backend.src.db_manager import DBManager
from backend.src.exceptions.users import IncorrectTokenException, ExpiredTokenException, AuthRequiredException
from backend.src.logs.logging_config import logging_configuration
from backend.src.models.users import UserModel
from backend.src.repositories.utils.users import decode_token
from backend.src.schemas.users import UserReadWithRole


async def get_db():
    async with DBManager(session_factory=async_session_maker) as db:
        yield db

DBDep = Annotated[DBManager, Depends(get_db)]


def get_token(request: Request) -> str:
    token = request.headers.get("Authorization", None)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Необходимо авторизоваться')

    return token.split(' ')[1]


def get_current_user(token: str = Depends(get_token)):
    try:
        data = decode_token(token)
    except IncorrectTokenException as ex:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ex.detail)
    except ExpiredTokenException as ex:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ex.detail)
    return UserReadWithRole.model_validate(
        data, from_attributes=True
    )


UserDep = Annotated[UserModel, Depends(get_current_user)]


def get_current_user_optional(request: Request):
    token = request.headers.get("Authorization", None)
    if token:
        return get_current_user(token.split(' ')[1])


OptionalUserDep = Annotated[UserModel, Depends(get_current_user_optional)]


def get_current_superuser(token: str = Depends(get_token)):
    try:
        data = decode_token(token)
    except IncorrectTokenException as ex:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ex.detail)
    except ExpiredTokenException as ex:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ex.detail)
    if data['is_superuser']:
        return UserReadWithRole.model_validate(
            data, from_attributes=True
        )
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Доступно только администраторам')


SuperuserDep = Annotated[UserModel, Depends(get_current_superuser)]
