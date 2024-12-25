from pydantic import BaseModel
from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError, NoResultFound

from backend.src.exceptions.base import ObjectAlreadyExistsException, ObjectNotFoundException


class BaseRepository:
    model = None
    schema: BaseModel = None

    def __init__(self, session):
        self.session = session

    async def get_filtered(self, *filter, **filter_by):
        """Получение отфильтрованного списка объектов по указанным параметрам."""
        stmt = (
            select(self.model)
            .filter(*filter)
            .filter_by(**filter_by)
        )
        result = await self.session.execute(stmt)
        result = result.scalars().all()
        if result:
            return [
                self.schema.model_validate(obj, from_attributes=True)
                for obj in result
            ]


    async def get_all(self, *args, **kwargs):
        """Получение списка объектов."""
        return await self.get_filtered()

    async def get_one_or_none(self, **filter_by):
        """Получение объекта или None."""
        stmt = select(self.model)
        stmt = stmt.filter_by(**filter_by)

        result = await self.session.execute(stmt)
        result = result.scalars().one_or_none()
        if result:
            return self.schema.model_validate(result, from_attributes=True)

    async def create(self, data: BaseModel):
        """Создание объекта."""
        try:
            new_obj_stmt = (
                insert(self.model)
                .values(**data.model_dump())
                .returning(self.model)
            )
            result = await self.session.execute(new_obj_stmt)
            result = result.scalars().one()
            return self.schema.model_validate(
                result, from_attributes=True)
        except IntegrityError:
            raise ObjectAlreadyExistsException

    async def bulk_create(self, data: list[BaseModel]):
        """Создание нескольких объектов через один запрос."""
        stmt = (
            insert(self.model)
            .values([obj.model_dump() for obj in data])
            .returning(self.model.id)
        )
        result = await self.session.execute(stmt)
        result = result.scalars().all()
        return result

    async def delete(self, **filter_by):
        """Удаление объекта."""
        stmt = delete(self.model).filter_by(**filter_by).returning(self.model)
        result = await self.session.execute(stmt)
        try:
            result.scalars().one()
        except NoResultFound:
            raise ObjectNotFoundException

    async def update(
        self,
        data: BaseModel,
        exclude_unset: bool = False,
        **filter_by
    ):
        """Обновление объекта."""
        stmt = (
            update(self.model)
            .filter_by(**filter_by)
            .values(**data.model_dump(exclude_unset=exclude_unset))
            .returning(self.model)
        )
        result = await self.session.execute(stmt)
        result = result.scalars().one_or_none()
        if result:
            return self.schema.model_validate(result, from_attributes=True)
