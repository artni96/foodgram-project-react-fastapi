from starlette import status

from backend.src.exceptions.users import IncorrectTokenException, ExpiredTokenException
from backend.src.models.users import UserModel
from backend.src.db_manager import DBManager

from typing import Annotated
# from backend.src.services.users import current_user, current_superuser
from fastapi import Depends
from backend.src.db import async_session_maker

from backend.src.repositories.utils.users import decode_token
from backend.src.schemas.users import UserRead, UserReadWithRole
# from backend.src.services.users import current_user, current_superuser, optional_current_user
from fastapi import Depends, Request, HTTPException
from backend.src.db import async_session_maker, session
from backend.src.repositories.users import UserRepository

async def get_db():
    async with DBManager(session_factory=async_session_maker) as db:
        yield db

# UserDep = Annotated[UserModel, Depends(current_user)]
DBDep = Annotated[DBManager, Depends(get_db)]


def get_token(request: Request) -> str:
    # token = request.cookies.get("access_token", None)
    token = request.headers.get("Authorization", None)
    # print(token)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Необходимо авторизоваться')
    return token.split(' ')[1]


def get_current_user(token: str = Depends(get_token)):
    try:
        data = decode_token(token)
    except IncorrectTokenException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Неверный JWT Token')
    except ExpiredTokenException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Необходимо авторизоваться')
    return UserReadWithRole.model_validate(
        data, from_attributes=True
    )


UserDep = Annotated[UserModel, Depends(get_current_user)]
# UserDep = Annotated[UserModel, Depends(current_user)]


def get_current_user_optional(request: Request):
    # token = request.cookies.get("access_token", None)
    token = request.headers.get("Authorization", None)
    if token:
        return get_current_user(token.split(' ')[1])


OptionalUserDep = Annotated[UserModel, Depends(get_current_user_optional)]
# OptionalUserDep = Annotated[UserModel, Depends(optional_current_user)]


def get_current_superuser(token: str = Depends(get_token)):
    try:
        data = decode_token(token)
    except IncorrectTokenException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Неверный JWT Token')
    except ExpiredTokenException as ex:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ex.detail)
    if data['is_superuser']:
        return UserReadWithRole.model_validate(
            data, from_attributes=True
        )
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Доступно только администраторам')


SuperuserDep = Annotated[UserModel, Depends(get_current_superuser)]
# SuperuserDep = Annotated[UserModel, Depends(current_superuser)]
