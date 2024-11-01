from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy import insert, select
from sqlalchemy.orm import load_only
from sqlalchemy.exc import IntegrityError

from backend.src.models.users import SubscriptionModel, UserModel
from backend.src.repositories.base import BaseRepository
from backend.src.schemas.subscriptions import SubscriptionCreate
from backend.src.schemas.users import BaseUserRead
from backend.src.db import engine


class SubscriptionRepository(BaseRepository):

    model = SubscriptionModel
    schema = BaseUserRead

    async def get_user_subscriptions_ids(self, user_id):
        author_ids = (
            select(self.model.author_id)
            .filter_by(subscriber_id=user_id)
            .subquery('author_ids'))
        user_subscriptions_stmt = (
            select(
                UserModel.id,
                UserModel.email,
                UserModel.username,
                UserModel.first_name,
                UserModel.last_name
            )
            .filter(UserModel.id.in_(author_ids))
            )
        result = await self.session.execute(user_subscriptions_stmt)
        return [
            BaseUserRead.model_validate(obj, from_attributes=True)
            for obj in result
        ]

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
