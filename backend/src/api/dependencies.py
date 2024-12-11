from starlette import status

from backend.src.exceptions.users import IncorrectTokenException
from backend.src.models.users import UserModel
from backend.src.db_manager import DBManager

from typing import Annotated

from backend.src.repositories.utils.users import decode_token
from backend.src.services.users import current_user, current_superuser
from fastapi import Depends, Request, HTTPException
from backend.src.db import async_session_maker, session
from backend.src.repositories.users import UserRepository


async def get_db():
    async with DBManager(session_factory=async_session_maker) as db:
        yield db


DBDep = Annotated[DBManager, Depends(get_db)]

def get_token(request: Request) -> str:
    token = request.cookies.get("access_token", None)
    if not token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    return token


def get_current_user_id(token: str = Depends(get_token)):
    try:
        data = decode_token(token)
        # data = PasswordManager().decode_token(token)
    except IncorrectTokenException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Неверный JWT Token')
        # raise IncorrectTokenHTTPException
    return data['id']
    # return UserForJWT.model_validate(data, from_attributes=True)
UserDep = Annotated[UserModel, Depends(get_current_user_id)]
