from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy import func, select

from backend.src.models.subscriptions import SubscriptionModel
from backend.src.models.users import UserModel
from backend.src.repositories.base import BaseRepository
from backend.src.repositories.utils.users import users_url_paginator
from backend.src.schemas.users import (FollowedUserRead, UserListRead,
                                       UserWithHashedPasswordRead)


class UserRepository(BaseRepository):
    model = UserModel
    schema = FollowedUserRead

    async def get_all(
        self,
        user_id: int,
        offset: int | None,
        limit: int,
        page: int

    ):
        user_list_stmt = (
            select(self.model)
            .order_by(self.model.id)
            .limit(limit)
        )
        if offset:
            user_list_stmt = user_list_stmt.offset(offset)
        users_count_stmt = (
            select(func.count('*').label('user_count'))
            .select_from(self.model)
        )
        sub_ids_stmt = (
            select(SubscriptionModel.author_id)
            .filter_by(subscriber_id=user_id)
            )
        sub_ids = await self.session.execute(sub_ids_stmt)
        sub_ids = sub_ids.scalars().all()
        user_list = await self.session.execute(user_list_stmt)
        user_list = user_list.scalars().all()
        users_count = await self.session.execute(users_count_stmt)
        users_count = users_count.scalars().one()
        user_list_result = list()
        for obj in user_list:
            current_obj = FollowedUserRead(
                username=obj.username,
                email=obj.email,
                id=obj.id,
                first_name=obj.first_name,
                last_name=obj.last_name
            )
            if obj.id not in sub_ids:
                current_obj.is_subscribed = False
            user_list_result.append(current_obj)
        paginator_values = await users_url_paginator(
            limit=limit,
            page=page,
            count=users_count
        )
        response = UserListRead(
            count=users_count,
            next=paginator_values['next'],
            previous=paginator_values['previous'],
            result=user_list_result
        )
        return response

    async def get_one_or_none(self, user_id, current_user_id=None):
        stmt = select(self.model).filter_by(id=user_id)

        user_result = await self.session.execute(stmt)
        user_result = user_result.scalars().one_or_none()

        if user_result:
            result = self.schema.model_validate(
                user_result,
                from_attributes=True
            )
            if current_user_id:
                if_subscribed_stmt = (
                    select(SubscriptionModel)
                    .select_from(SubscriptionModel)
                    .filter_by(
                        author_id=user_id,
                        subscriber_id=current_user_id
                    )
                )
                if_subscribed_result = await self.session.execute(
                    if_subscribed_stmt)
                if_subscribed_result = (
                    if_subscribed_result.scalars().one_or_none()
                )
                if not if_subscribed_result:
                    result.is_subscribed = False
                    return result
                return result
            return result
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Пользователь не найден.'
        )

    async def get_user_hashed_password(self, user_id):
        hashed_password_stmt = (
            select(
                self.model)
            .select_from(self.model)
            .filter_by(id=user_id)
        )
        result = await self.session.execute(hashed_password_stmt)
        result = result.scalars().one_or_none()
        if result:
            return UserWithHashedPasswordRead.model_validate(
                result,
                from_attributes=True
            )
