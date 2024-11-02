from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy import func, insert, select
from sqlalchemy.exc import IntegrityError

from backend.src.models.users import SubscriptionModel, UserModel
from backend.src.repositories.base import BaseRepository
from backend.src.repositories.utils.subscriptions import subs_url_paginator
from backend.src.schemas.subscriptions import (SubscriptionCreate,
                                               SubscriptionRead)
from backend.src.schemas.users import FollowedUserRead


class SubscriptionRepository(BaseRepository):

    model = SubscriptionModel
    schema = FollowedUserRead

    async def get_user_subs(
        self,
        user_id: int,
        offset: int,
        limit: int
    ):
        author_ids = (
            select(self.model.author_id)
            .filter_by(subscriber_id=user_id)
            .subquery('author_ids'))
        user_subs_count_stmt = (
            select(
                func.count('*').label('subs_count')
            )
            .select_from(self.model)
            .filter_by(subscriber_id=user_id)
            .group_by(self.model.subscriber_id)
        )
        user_subs_count = await self.session.execute(user_subs_count_stmt)
        user_subs_count = user_subs_count.scalars().one()
        user_subs_stmt = (
            select(
                UserModel.id,
                UserModel.email,
                UserModel.username,
                UserModel.first_name,
                UserModel.last_name,
            )
            .filter(UserModel.id.in_(author_ids))
            .limit(limit)
            )
        if offset:
            user_subs_stmt = user_subs_stmt.offset(offset)
        user_subs_result = await self.session.execute(user_subs_stmt)
        user_subs_result = user_subs_result.mappings().all()
        paginator_values = await subs_url_paginator(
            limit=limit,
            page=offset,
            count=user_subs_count
        )
        response = SubscriptionRead(
            count=user_subs_count,
            next=paginator_values['next'],
            previous=paginator_values['previous'],
            result=user_subs_result
        )
        return response

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
