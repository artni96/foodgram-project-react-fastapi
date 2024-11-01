from backend.src.models.users import UserModel
from backend.src.db_manager import DBManager

from typing import Annotated
from backend.src.services.users import current_user
from fastapi import Depends
from backend.src.db import async_session_maker


async def get_db():
    async with DBManager(session_factory=async_session_maker) as db:
        yield db

UserDep = Annotated[UserModel, Depends(current_user)]
DBDep = Annotated[DBManager, Depends(get_db)]
