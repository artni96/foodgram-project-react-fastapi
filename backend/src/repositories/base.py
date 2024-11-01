from sqlalchemy import insert, select, delete
from pydantic import BaseModel
from backend.src.db import engine
from fastapi import HTTPException
from sqlalchemy.exc import NoResultFound
from fastapi import status


class BaseRepository:
    model = None
    schema: BaseModel = None

    def __init__(self, session):
        self.session = session

    async def get_one_or_none(self, **filter_by):
        stmt = select(self.model)
        stmt = stmt.filter_by(**filter_by)
        print(stmt.compile(
            engine,
            compile_kwargs={"literal_binds": True})
        )

        result = await self.session.execute(stmt)
        result = result.scalars().one_or_none()
        if result:
            return self.schema.model_validate(result, from_attributes=True)

    async def create(self, data: BaseModel):
        new_obj_stmt = (
            insert(self.model)
            .values(**data.model_dump())
            .returning(self.model)
        )
        result = await self.session.execute(new_obj_stmt)
        return self.schema.model_validate(
            result.scalars().one(), from_attributes=True)

    async def delete(self, **filter_by):
        try:
            stmt = delete(self.model).filter_by().returning(self.model)
            result = await self.session.execute(stmt)
            result = result.scalars().one()
        except NoResultFound:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Пользователь не найден.'
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Не удалось отписаться от пользователя'
            )
