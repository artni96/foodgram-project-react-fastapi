from sqlalchemy import insert, select
from pydantic import BaseModel
from backend.src.db import engine


class BaseRepository:
    model = None
    schema: BaseModel = None

    def __init__(self, session):
        self.session = session

    async def get_one_or_none(self, **filter_by):
        stmt = select(self.model)
        if 'id' in filter_by:
            stmt = stmt.filter_by(id=filter_by['id'])
        print(stmt.compile(
            engine,
            compile_kwargs={"literal_binds": True})
        )

        result = await self.session.execute(stmt)
        return self.schema.model_validate(result.scalars().one(), from_attributes=True)
        return result.scalars().one_or_none()

    async def create(self, values: BaseModel):
        new_obj_stmt = (
            insert(self.model)
            .values(**values.model_dump())
            .returning(self.model)
        )
        result = await self.session.execute(new_obj_stmt)
        return self.schema.model_validate(
            result.scalars().one(), from_attributes=True)