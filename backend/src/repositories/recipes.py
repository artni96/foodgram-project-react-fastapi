import os
import pathlib

from fastapi import HTTPException, status
from sqlalchemy import and_, delete, insert, select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import NoResultFound

from backend.src.constants import DOMAIN_ADDRESS, MOUNT_PATH
from backend.src.models.ingredients import (IngredientAmountModel,
                                            IngredientModel,
                                            RecipeIngredientModel)
from backend.src.models.recipes import (FavoriteRecipeModel, ImageModel,
                                        RecipeModel, ShoppingCartModel)
from backend.src.models.subscriptions import SubscriptionModel
from backend.src.models.tags import RecipeTagModel, TagModel
from backend.src.models.users import UserModel
from backend.src.repositories.base import BaseRepository
from backend.src.repositories.utils.ingredients import \
    check_ingredient_duplicates_for_recipe
from backend.src.repositories.utils.paginator import url_paginator
from backend.src.schemas.recipes import (CheckRecipeRead, ImageRead,
                                         RecipeCreate, RecipeCreateRequest,
                                         RecipeListRead, RecipeRead,
                                         RecipeUpdate, RecipeUpdateRequest)
from backend.src.schemas.users import FollowedUserRead
from backend.src.utils.image_manager import ImageManager


class ImageRepository(BaseRepository):
    model = ImageModel
    schema = ImageRead


class RecipeRepository(BaseRepository):
    model = RecipeModel
    schema = RecipeRead

    async def get_filtered(
            self,
            current_user,
            is_favorited,
            is_in_shopping_cart,
            tags,
            author,
            db,
            limit,
            page,
            router_prefix
    ):
        """Получение отфильтрованного списка рецептов."""
        filtered_recipe_id_list_stmt = (
            select(
                self.model.id
            )
            .join(
                UserModel,
                UserModel.id == self.model.author
            )
            .outerjoin(
                SubscriptionModel,
                and_(
                    UserModel.id == SubscriptionModel.subscriber_id,
                    self.model.author == SubscriptionModel.author_id
                )
            )
            .join(
                RecipeTagModel,
                RecipeTagModel.recipe_id == self.model.id
            )
            .join(
                TagModel,
                TagModel.id == RecipeTagModel.tag_id
            )

        )
        # filtered_recipe_id_list = await self.session.execute(
        #     filtered_recipe_id_list_stmt
        # )
        # filtered_recipe_id_list = (
        #     filtered_recipe_id_list.unique().scalars().all()
        # )
        # recipe_count = len(filtered_recipe_id_list)
        if current_user:
            if is_favorited:
                filtered_recipe_id_list_stmt = (
                    filtered_recipe_id_list_stmt.join(
                        FavoriteRecipeModel,
                        and_(
                            FavoriteRecipeModel.recipe_id == self.model.id,
                            FavoriteRecipeModel.user_id == current_user.id
                        )
                    )
                )
            if is_in_shopping_cart:
                filtered_recipe_id_list_stmt = (
                    filtered_recipe_id_list_stmt.join(
                        ShoppingCartModel,
                        and_(
                            ShoppingCartModel.recipe_id == self.model.id,
                            ShoppingCartModel.user_id == current_user.id
                        )
                    )
                )
        if tags:
            filtered_recipe_id_list_stmt = filtered_recipe_id_list_stmt.filter(
                TagModel.slug.in_(tags)
            )
        if author:
            filtered_recipe_id_list_stmt = filtered_recipe_id_list_stmt.filter(
                self.model.author == author
            )
        recipe_id_list = await self.session.execute(
            filtered_recipe_id_list_stmt
        )
        recipe_id_list_result = recipe_id_list.unique().scalars().all()
        _from, _to = (page-1)*limit, (page-1)*limit+limit
        filtered_recipe_id_list = recipe_id_list_result[_from:_to]
        filtered_recipe_list = list()
        for recipe_id in filtered_recipe_id_list:
            filtered_recipe_list.append(
                await self.get_one_or_none(
                    current_user=current_user,
                    id=recipe_id,
                    db=db
                )
            )
        recipes_count = len(recipe_id_list_result)
        paginator_values = url_paginator(
            limit=limit,
            page=page,
            count=recipes_count,
            router_prefix=router_prefix
        )
        result = RecipeListRead(
            count= recipes_count,
            next=paginator_values['next'],
            previous=paginator_values['previous'],
            result=filtered_recipe_list
        )
        return result

    async def get_one_or_none(self, id, current_user, db):
        """Получение репепта по id если он существует."""
        try:
            ingredient_list_stmt = (
                select(
                    IngredientAmountModel.amount,
                    IngredientModel.id,
                    IngredientModel.measurement_unit,
                    IngredientModel.name
                )
                .filter(RecipeIngredientModel.recipe_id == id)
            ).outerjoin(
                RecipeIngredientModel,
                IngredientAmountModel.id == (
                    RecipeIngredientModel.ingredient_amount_id
                )
            ).outerjoin(
                IngredientModel,
                IngredientModel.id == IngredientAmountModel.ingredient_id
            )

            ingredient_list_result = await self.session.execute(
                ingredient_list_stmt
            )
            ingredient_list_result = (
                ingredient_list_result.unique().mappings().all()
            )
            recipe_body_stmt = (
                select(
                    self.model
                )
                .filter(
                    RecipeModel.id==id,
                    # ShoppingCartModel.user_id == current_user.id,
                    # # FavoriteRecipeModel.user_id == current_user.id
                )
                .options(
                    selectinload(self.model.tags),
                    selectinload(self.model.author_info)
                    .load_only(
                        UserModel.username,
                        UserModel.id,
                        UserModel.first_name,
                        UserModel.last_name,
                        UserModel.email,
                    )
                    ,
                    selectinload(self.model.is_favorited),
                    selectinload(self.model.is_in_shopping_cart)
                )
                # .outerjoin(
                #     FavoriteRecipeModel,
                #     FavoriteRecipeModel.user_id == RecipeModel.author
                # )
                # .outerjoin(
                #     ShoppingCartModel,
                #     ShoppingCartModel.user_id == RecipeModel.author
                # )

            )
            recipe_body_result = await self.session.execute(recipe_body_stmt)
            recipe_body_result = recipe_body_result.scalars().one()
            # print(recipe_body_result.is_in_shopping_cart[0].user_id)
            recipe_image = await db.images.get_one_or_none(
                id=recipe_body_result.image
            )
            recipe_image_url = (
                    f'{DOMAIN_ADDRESS}{MOUNT_PATH}'
                    f'/{recipe_image.name}'
                )
            author_schema_response = FollowedUserRead.model_validate(
                recipe_body_result.author_info, from_attributes=True
            )
            if current_user:
                if current_user.id == recipe_body_result.author_info.id:
                    author_schema_response.is_subscribed = False
                else:
                    subs = await db.subscriptions.get_one_or_none(
                        author_id=recipe_body_result.author_info.id,
                        subscriber_id=current_user.id
                    )
                    if not subs:
                        author_schema_response.is_subscribed = False
            else:
                author_schema_response.is_subscribed = False
            response = self.schema(
                id=recipe_body_result.id,
                tags=recipe_body_result.tags,
                author=author_schema_response,
                ingredients=ingredient_list_result,
                name=recipe_body_result.name,
                image=recipe_image_url,
                text=recipe_body_result.text,
                cooking_time=recipe_body_result.cooking_time
            )
            if current_user:
                if recipe_body_result.is_favorited:
                    response.is_favorited = True
                if recipe_body_result.is_in_shopping_cart:
                    response.is_in_shopping_cart = True
            return response
        except NoResultFound:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Рецепт не найден.'
            )

    async def create(self, recipe_data: RecipeCreateRequest, db, current_user_id: int):
        """Создание нового рецепта."""
        _recipe_data = RecipeCreate(
            **recipe_data.model_dump(),
            author=current_user_id,
        )
        try:
            image_base64 = _recipe_data.image
            generated_image_name = ImageManager().create_random_name(image_base64)
            # print(generated_image_name)
            while await self.check_image_name(generated_image_name):
                generated_image_name = ImageManager().create_random_name(image_base64)

            image_url = (
                f'{DOMAIN_ADDRESS}{MOUNT_PATH}'
                f'/{generated_image_name}'
            )
            image_id = await self.create_image(
                name=generated_image_name,
                base64=image_base64
            )
            _recipe_data.image = image_id
            new_obj_stmt = (
                insert(self.model)
                .values(**_recipe_data.model_dump())
                .returning(self.model)
            )
            recipe_result = await self.session.execute(new_obj_stmt)
            recipe_result = recipe_result.scalars().one()
            user_result = await db.users.get_one_or_none(
                user_id=recipe_result.author,
                current_user_id=recipe_result.id
            )

        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Проверьте поля name, text, cooking_time, image'
            )
        ingredients_data = recipe_data.ingredients
        ingredients_result = list()
        if ingredients_data:
            try:
                _ingredients_data = (
                    await check_ingredient_duplicates_for_recipe(
                        ingredients_data=ingredients_data
                    )
                )
                ingredients_result = (
                    await db.ingredients_amount.add_recipe_ingredients(
                        ingredients_data=_ingredients_data,
                        db=db,
                        recipe_id=recipe_result.id
                    )
                )
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='Указанных ингредиентов нет в БД.'
                )
        tags_data = set(recipe_data.tags)
        tags_result = list()
        if tags_data:
            try:
                tags_result = await db.recipe_tags.create(
                    tags_data=tags_data,
                    db=db,
                    recipe_id=recipe_result.id
                )
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='Указанных тегов нет в БД.'
                )
        # print(generated_image_name)
        ImageManager().base64_to_file(
            base64_string=image_base64,
            image_name=generated_image_name)
        response = self.schema(
            name=recipe_result.name,
            text=recipe_result.text,
            cooking_time=recipe_result.cooking_time,
            author=user_result,
            id=recipe_result.id,
            tags=tags_result,
            ingredients=ingredients_result,
            image=image_url
        )
        return response

    async def update(self, recipe_data: RecipeUpdateRequest, db, id: int):
        """Обновление рецепта по его id."""
        _recipe_data = RecipeUpdate(
            **recipe_data.model_dump(),
            id=id
        )
        try:
            recipe_image_id_stmt = (
                select(RecipeModel.image)
                .filter_by(id=_recipe_data.id)
                .scalar_subquery()
                # .subquery.label('recipe_image_id')
            )
            image_stmt = (
                select(
                    ImageModel
                )
                .filter(
                    ImageModel.id == recipe_image_id_stmt,
                    ImageModel.base64 == _recipe_data.image)
            )
            image_result = await self.session.execute(image_stmt)
            image_result = image_result.scalars().one_or_none()
            if not image_result:
                recipe_image_update_stmt = (
                    update(ImageModel)
                    .filter_by(id=recipe_image_id_stmt)
                    .values(base64=_recipe_data.image)
                    .returning(ImageModel.name, ImageModel.id)
                )
                current_image = await self.session.execute(
                    recipe_image_update_stmt
                )
                current_image = current_image.mappings().one_or_none()
                media_path = pathlib.Path(__file__).parent.parent.resolve()
                image_to_delete = (
                    f'{media_path}{MOUNT_PATH}/{current_image.name}'
                )
                if os.path.exists(image_to_delete):
                    os.remove(image_to_delete)
                image_base64 = _recipe_data.image
                _recipe_data.image = current_image.id
                image_name = ImageManager().base64_to_file(
                    base64_string=image_base64,
                    image_name=current_image.name)

            else:
                _recipe_data.image = image_result.id
                image_name = image_result.name
            image_url = (
                f'{DOMAIN_ADDRESS}{MOUNT_PATH}'
                f'/{image_name}'
            )
            obj_update_stmt = (
                update(self.model)
                .filter_by(id=_recipe_data.id)
                .values(**_recipe_data.model_dump())
                .returning(self.model)
            )
            updated_recipe_result = await self.session.execute(obj_update_stmt)
            updated_recipe_result = updated_recipe_result.scalars().one()
            user_result = await db.users.get_one_or_none(
                user_id=updated_recipe_result.author,
                current_user_id=updated_recipe_result.id
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Проверьте поля name, text, cooking_time, image'
            )
        ingredients_data = recipe_data.ingredients
        ingredients_result = list()
        if ingredients_data:
            try:
                _ingredients_data = (
                    await check_ingredient_duplicates_for_recipe(
                        ingredients_data=ingredients_data
                    )
                )
                ingredients_result = (
                    await db.ingredients_amount.change_recipe_ingredients(
                        ingredients_data=_ingredients_data,
                        recipe_id=id,
                        db=db
                    )
                )
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='Указанных ингредиентов нет в БД.'
                )

        tags_data = set(recipe_data.tags)
        tags_result = list()
        if tags_data:
            try:
                tags_result = await db.recipe_tags.update(
                    tags_data=tags_data,
                    db=db,
                    recipe_id=id
                )
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='Указанных тегов нет в БД.'
                )
        response = self.schema(
            name=updated_recipe_result.name,
            text=updated_recipe_result.text,
            cooking_time=updated_recipe_result.cooking_time,
            author=user_result,
            id=updated_recipe_result.id,
            tags=tags_result,
            ingredients=ingredients_result,
            image=image_url
        )
        return response

    async def delete(self, id):
        """Удаление рецепта по его id."""
        recipe_ingredient_amount_ids_stmt = (
            select(RecipeIngredientModel.ingredient_amount_id)
            .filter_by(recipe_id=id)
        )
        recipe_ingredient_amount_ids = await self.session.execute(
            recipe_ingredient_amount_ids_stmt
        )
        recipe_ingredient_amount_ids = (
            recipe_ingredient_amount_ids.scalars().all()
        )
        recipe_to_delete_stmt = (
            delete(self.model)
            .filter_by(id=id)
            .returning(self.model.image)
        )
        recipe_image_id = await self.session.execute(recipe_to_delete_stmt)
        recipe_image_id = recipe_image_id.scalars().one()
        recipe_image_to_delete_stmt = (
            delete(ImageModel)
            .filter_by(id=recipe_image_id)
            .returning(ImageModel.name)
        )
        image_name_to_delete = await self.session.execute(
            recipe_image_to_delete_stmt
        )
        image_name_to_delete = image_name_to_delete.scalars().one()
        media_path = pathlib.Path(__file__).parent.parent.resolve()
        image_to_delete = (
            f'{media_path}{MOUNT_PATH}/{image_name_to_delete}'
        )
        # print(image_to_delete)
        if os.path.exists(image_to_delete):
            os.remove(image_to_delete)
        recipe_ingredient_amount_ids_to_delete = list()
        for id in recipe_ingredient_amount_ids:
            current_obj_stmt = (
                select(RecipeIngredientModel.ingredient_amount_id)
                .filter_by(ingredient_amount_id=id)
            )
            current_obj = await self.session.execute(current_obj_stmt)
            current_obj = current_obj.scalars().one_or_none()
            if not current_obj:
                recipe_ingredient_amount_ids_to_delete.append(id)
        if recipe_ingredient_amount_ids_to_delete:
            ids_to_delete = (
                delete(IngredientAmountModel)
                .filter(IngredientAmountModel.id.in_(
                    recipe_ingredient_amount_ids_to_delete
                )
                )
            )
            await self.session.execute(ids_to_delete)

    async def check_image_name(self, new_image_name: str):
        """Проверка уникальности названия картинки."""
        image_stmt = select(ImageModel).filter_by(name=new_image_name)
        result = await self.session.execute(image_stmt)
        return result.scalars().one_or_none()

    async def create_image(self, name, base64):
        """Создание записи в БД с данными (названием и
         исходных base64) новой картинки."""
        image_stmt = insert(ImageModel).values(
            {'name': name, 'base64': base64}
        ).returning(ImageModel.id)
        image_result = await self.session.execute(image_stmt)
        return image_result.scalars().one()

    async def check_recipe_exists(self, id: int):
        """Проверка на наличие рецепта в бд с указанным id."""
        stmt = select(self.model.author, self.model.id).filter_by(id=id)
        result = await self.session.execute(stmt)
        result = result.mappings().one_or_none()
        if result:
            return CheckRecipeRead.model_validate(result, from_attributes=True)
