from sqlalchemy import insert, select
from fastapi import HTTPException

from backend.src.models.users import SubscriptionModel, UserModel
from backend.src.repositories.base import BaseRepository
from backend.src.schemas.users import (BaseUserRead, SubscriptionCreate,
                                       SubscriptionResponse)
from sqlalchemy.exc import IntegrityError
from http import HTTPStatus


class SubscriptionRepository(BaseRepository):

    model = SubscriptionModel
    schema = BaseUserRead

    async def create(self, data: SubscriptionCreate):
        try:
            subscription_stmt = (
                insert(self.model)
                .values(**data.model_dump())
                .returning(self.model.author_id)
            )
            new_sub_result = await self.session.execute(subscription_stmt)
            new_sub_result = new_sub_result.scalars().one()
            user_info_stmt = (
                select(
                    UserModel.id,
                    UserModel.email,
                    UserModel.username,
                    UserModel.first_name,
                    UserModel.last_name
                )
                .select_from(UserModel)
                .filter_by(id=new_sub_result)
            )
            user_info_response = await self.session.execute(user_info_stmt)
            return self.schema.model_validate(
                user_info_response.mappings().one(),
                from_attributes=True
            )

        except IntegrityError as e:
            print(e.__cause__)
            if 'ForeignKeyViolationError' in str(e.__cause__):
                raise HTTPException(
                    status_code=HTTPStatus.NOT_FOUND,
                    detail='Пользователь не найден!'
                )
            elif 'UniqueViolationError' in str(e.__cause__):
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail='Вы уже подписанны на данного пользователя!'
                )
