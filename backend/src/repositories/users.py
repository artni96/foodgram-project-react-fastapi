from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy import select

from backend.src.models.users import SubscriptionModel, UserModel
from backend.src.repositories.base import BaseRepository
from backend.src.schemas.users import (ExpendedUserRead,
                                       UserWithHashedPasswordRead)


class UserRepository(BaseRepository):
    model = UserModel
    schema = ExpendedUserRead

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
                if if_subscribed_result:
                    result.is_subscribed = True
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
