from asyncpg import ForeignKeyViolationError, UniqueViolationError
from sqlalchemy import delete, func, insert, select
from sqlalchemy.exc import NoResultFound, IntegrityError
from sqlalchemy.orm import load_only

from backend.src.constants import MAIN_URL, MOUNT_PATH
from backend.src.exceptions.subscriptions import UniqueConstraintSubscriptionException, FollowingYourselfException, \
    SubscriptionNotFoundException
from backend.src.exceptions.users import UserNotFoundException
from backend.src.models.recipes import RecipeModel
from backend.src.models.subscriptions import SubscriptionModel
from backend.src.models.users import UserModel
from backend.src.repositories.base import BaseRepository
from backend.src.repositories.utils.paginator import url_paginator
from backend.src.schemas.subscriptions import (SubscriptionCreate,
                                               SubscriptionListRead)
from backend.src.schemas.users import (FollowedUserRead,
                                       FollowedUserWithRecipiesRead,
                                       ShortRecipeRead)


class SubscriptionRepository(BaseRepository):

    model = SubscriptionModel
    schema = FollowedUserRead

    async def get_user_subs(
        self,
        user_id: int,
        offset: int,
        limit: int,
        page: int,
        recipes_limit: int,
        router_prefix: str
    ):
        """Получение списка подписок пользователя."""
        author_ids = (
            select(self.model.author_id)
            .filter_by(subscriber_id=user_id)
            .scalar_subquery()
        )
        user_subs_count_stmt = (
            select(
                func.coalesce(func.count('*').label('subs_count'), 0)
            )
            .select_from(self.model)
            .filter_by(subscriber_id=user_id)
            .group_by(self.model.subscriber_id)
        )
        user_subs_count = await self.session.execute(user_subs_count_stmt)
        user_subs_count = user_subs_count.scalars().one_or_none()
        if not user_subs_count:
            user_subs_count = 0
        user_subs_stmt = (
            select(
                UserModel
            )
            .filter(UserModel.id.in_(author_ids))
            .limit(limit)
            .outerjoin(RecipeModel, RecipeModel.author == UserModel.id)
            .options(
                load_only(
                    UserModel.id,
                    UserModel.email,
                    UserModel.username,
                    UserModel.first_name,
                    UserModel.last_name,
                )
                .selectinload(UserModel.recipe).load_only(
                    RecipeModel.id,
                    RecipeModel.name,
                    RecipeModel.image,
                    RecipeModel.cooking_time
                )
                .selectinload(RecipeModel.image_info)
            )
        )
        if offset:
            user_subs_stmt = user_subs_stmt.offset(offset)
        user_subs_result = await self.session.execute(user_subs_stmt)
        user_subs_result = user_subs_result.unique().scalars().all()
        paginator_values = url_paginator(
            limit=limit,
            page=page,
            count=user_subs_count,
            router_prefix=router_prefix
        )
        result_list = list()
        for obj in user_subs_result:
            recipe_list = list()
            for recipe in obj.recipe:
                recipe_list.append(
                    ShortRecipeRead(
                        image=(
                            f'{MAIN_URL}{MOUNT_PATH}/{recipe.image_info.name}'
                        ),
                        id=recipe.id,
                        name=recipe.name,
                        cooking_time=recipe.cooking_time
                    )
                )
            result_list.append(
                FollowedUserWithRecipiesRead(
                    email=obj.email,
                    id=obj.id,
                    username=obj.username,
                    first_name=obj.first_name,
                    last_name=obj.last_name,
                    is_subscribed=True,
                    recipes=recipe_list[:recipes_limit],
                    recipes_count=len(recipe_list)
                )
            )
        response = SubscriptionListRead(
            count=user_subs_count,
            next=paginator_values['next'],
            previous=paginator_values['previous'],
            results=result_list
        )
        return response

    async def create(self, data: SubscriptionCreate, recipes_limit: int):
        """Создание подписки."""
        if data.author_id == data.subscriber_id:
            raise FollowingYourselfException
        try:
            subscription_stmt = (
                insert(self.model)
                .values(**data.model_dump())
                .returning(self.model.author_id)
            )
            new_sub_result = await self.session.execute(subscription_stmt)
            new_sub_result = new_sub_result.scalars().one()
        except IntegrityError as ex:
            if isinstance(ex.orig.__cause__, ForeignKeyViolationError):
                raise UserNotFoundException
            elif isinstance(ex.orig.__cause__, UniqueViolationError):
                raise UniqueConstraintSubscriptionException
        user_info_stmt = (
            select(
                UserModel
            )
            .filter(UserModel.id == new_sub_result)
            .outerjoin(RecipeModel, RecipeModel.author == UserModel.id)
            .options(
                load_only(
                    UserModel.id,
                    UserModel.email,
                    UserModel.username,
                    UserModel.first_name,
                    UserModel.last_name,
                )
                .selectinload(UserModel.recipe).load_only(
                    RecipeModel.id,
                    RecipeModel.name,
                    RecipeModel.image,
                    RecipeModel.cooking_time
                )
                .selectinload(RecipeModel.image_info)
            )
        )


        user_info = await self.session.execute(user_info_stmt)
        user_info = user_info.unique().scalars().one()
        recipe_list = list()
        if user_info.recipe:
            for recipe in user_info.recipe:
                recipe_list.append(
                    ShortRecipeRead(
                        image=(
                            f'{MAIN_URL}{MOUNT_PATH}/{recipe.image_info.name}'
                        ),
                        id=recipe.id,
                        name=recipe.name,
                        cooking_time=recipe.cooking_time
                    )
                )
        sub_response = FollowedUserWithRecipiesRead(
            email=user_info.email,
            id=user_info.id,
            username=user_info.username,
            first_name=user_info.first_name,
            last_name=user_info.last_name,
            is_subscribed=True,
            recipes=recipe_list[:recipes_limit],
            recipes_count=len(recipe_list)
        )
        return sub_response

    async def delete(self, **filter_by):
        """Удаление подписки."""
        stmt = delete(self.model).filter_by(**filter_by).returning(self.model)
        sub_to_delete = await self.session.execute(stmt)
        try:
            return sub_to_delete.scalars().one()
        except NoResultFound:
            raise SubscriptionNotFoundException
