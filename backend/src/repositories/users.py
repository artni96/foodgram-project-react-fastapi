from datetime import datetime, timezone, timedelta
from http import HTTPStatus

from fastapi import HTTPException
import jwt
from passlib.context import CryptContext
from sqlalchemy import func, select
from sqlalchemy.exc import NoResultFound

from backend.src.config import settings
from backend.src.exceptions.users import EmailNotRegisteredException, IncorrectPasswordException, \
    IncorrectTokenException
from backend.src.models.subscriptions import SubscriptionModel
from backend.src.models.users import UserModel
from backend.src.repositories.base import BaseRepository
from backend.src.repositories.utils.paginator import url_paginator
from backend.src.schemas.users import (FollowedUserRead, UserCreateResponse,
                                       UserListRead,
                                       UserWithHashedPasswordRead)


class UserRepository(BaseRepository):
    model = UserModel
    schema = UserCreateResponse

    async def get_all(
        self,
        limit: int,
        page: int,
        router_prefix: str,
        user_id: int | None = None,
        offset: int | None = None,
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
        if user_id:
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
            if user_id:
                if obj.id not in sub_ids:
                    current_obj.is_subscribed = False
            else:
                current_obj.is_subscribed = False
            user_list_result.append(current_obj)
        paginator_values = url_paginator(
            limit=limit,
            page=page,
            count=users_count,
            router_prefix=router_prefix
        )
        response = UserListRead(
            count=users_count,
            next=paginator_values['next'],
            previous=paginator_values['previous'],
            result=user_list_result
        )
        return response

    async def get_one(self, **filter_by):
        stmt = select(
            self.model.id,
            self.model.first_name,
            self.model.last_name,
            self.model.username,
            self.model.email
        ).filter_by(**filter_by)
        result = await self.session.execute(stmt)
        try:
            result = result.mappings().one()
            return self.schema.model_validate(result, from_attributes=True)
        except NoResultFound:
            raise EmailNotRegisteredException

    async def get_one_or_none(self, user_id, current_user_id=None):
        stmt = select(self.model).filter_by(id=user_id)

        user_result = await self.session.execute(stmt)
        user_result = user_result.scalars().one_or_none()

        if user_result:
            result = FollowedUserRead.model_validate(
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
            result.is_subscribed = False
            return result

    async def get_user_hashed_password(self, **filter_by):
        hashed_password_stmt = (
            select(
                self.model)
            .select_from(self.model)
            .filter_by(**filter_by)
        )
        result = await self.session.execute(hashed_password_stmt)
        result = result.scalars().one_or_none()
        if result:
            return UserWithHashedPasswordRead.model_validate(
                result,
                from_attributes=True
            )
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async def create_access_token(self, data) -> str:
        user = await self.get_user_hashed_password(email=data.email)
        if not user:
            raise EmailNotRegisteredException
        if not self.verify_password(data.password, user.hashed_password):
            raise IncorrectPasswordException
        to_encode = user.model_dump()
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode |= {"exp": expire}
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def decode_token(token: str) -> dict:
        try:
            return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        except jwt.exceptions.DecodeError:
            raise IncorrectTokenException
        except jwt.exceptions.ExpiredSignatureError:
            raise IncorrectTokenException

    # async def register_user(self, data: UserRequestAdd):
    #     hashed_password = self.hash_password(data.password)
    #     new_user_data = UserAdd(hashed_password=hashed_password, **data.model_dump())
    #     try:
    #         new_user = await self.db.users.add(new_user_data)
    #         await self.db.commit()
    #         return new_user
    #     except ObjectAlreadyExistsException as ex:
    #         raise UserAlreadyExistsException from ex

    # async def login_user(self, data: UserLoginRequest) -> str:
    #     user = await self.db.users.get_user_with_hashed_password(email=data.email)
    #     if not user:
    #         raise EmailNotRegisteredException
    #     if not self.verify_password(data.password, user.hashed_password):
    #         raise IncorrectPasswordException
    #     access_token = await self.create_access_token({"user_id": user.id})
    #     return access_token