import os
import pathlib

from fastapi import HTTPException, status
from loguru import logger
from sqlalchemy import and_, delete, insert, select, update, desc
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import selectinload

from backend.src.constants import MAIN_URL, MOUNT_PATH
from backend.src.exceptions.ingredients import IngredientNotFoundException
from backend.src.exceptions.recipes import (
    MainDataRecipeAtModifyingException,
    RecipeNotFoundException,
)
from backend.src.exceptions.tags import TagNotFoundException
from backend.src.models.ingredients import (
    IngredientAmountModel,
    IngredientModel,
    RecipeIngredientModel,
)
from backend.src.models.recipes import (
    FavoriteRecipeModel,
    ImageModel,
    RecipeModel,
    ShoppingCartModel,
)
from backend.src.models.subscriptions import SubscriptionModel
from backend.src.models.tags import RecipeTagModel, TagModel
from backend.src.models.users import UserModel
from backend.src.repositories.base import BaseRepository
from backend.src.repositories.utils.ingredients import (
    check_ingredient_duplicates_for_recipe,
)
from backend.src.repositories.utils.paginator import url_paginator
from backend.src.schemas.recipes import (
    CheckRecipeRead,
    ImageRead,
    RecipeCreate,
    RecipeCreateRequest,
    RecipeListRead,
    RecipeRead,
    RecipeUpdateRequest,
)
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
        router_prefix,
    ):
        """Получение отфильтрованного списка рецептов."""
        filtered_recipe_id_list_stmt = (
            select(self.model.id)
            .join(UserModel, UserModel.id == self.model.author)
            .outerjoin(
                SubscriptionModel,
                and_(
                    UserModel.id == SubscriptionModel.subscriber_id,
                    self.model.author == SubscriptionModel.author_id,
                ),
            )
            .join(RecipeTagModel, RecipeTagModel.recipe_id == self.model.id)
            .join(TagModel, TagModel.id == RecipeTagModel.tag_id)
        )
        if current_user:
            if is_favorited:
                filtered_recipe_id_list_stmt = filtered_recipe_id_list_stmt.join(
                    FavoriteRecipeModel,
                    and_(
                        FavoriteRecipeModel.recipe_id == self.model.id,
                        FavoriteRecipeModel.user_id == current_user.id,
                    ),
                )
            if is_in_shopping_cart:
                filtered_recipe_id_list_stmt = filtered_recipe_id_list_stmt.join(
                    ShoppingCartModel,
                    and_(
                        ShoppingCartModel.recipe_id == self.model.id,
                        ShoppingCartModel.user_id == current_user.id,
                    ),
                )
        if tags:
            filtered_recipe_id_list_stmt = filtered_recipe_id_list_stmt.filter(
                TagModel.slug.in_(tags)
            )
        if author:
            filtered_recipe_id_list_stmt = filtered_recipe_id_list_stmt.filter(
                self.model.author == author
            ).order_by(desc("id"))
        recipe_id_list = await self.session.execute(filtered_recipe_id_list_stmt)
        recipe_id_list_result = recipe_id_list.unique().scalars().all()
        _from, _to = (page - 1) * limit, (page - 1) * limit + limit
        filtered_recipe_id_list = recipe_id_list_result[_from:_to]
        filtered_recipe_list = list()
        for recipe_id in filtered_recipe_id_list:
            filtered_recipe_list.append(
                await self.get_one_or_none(
                    current_user=current_user, id=recipe_id, db=db
                )
            )
        recipes_count = len(recipe_id_list_result)
        paginator_values = url_paginator(
            limit=limit, page=page, count=recipes_count, router_prefix=router_prefix
        )
        result = RecipeListRead(
            count=recipes_count,
            next=paginator_values["next"],
            previous=paginator_values["previous"],
            results=filtered_recipe_list,
        )
        return result

    async def get_one_or_none(self, id, current_user, db):
        """Получение репепта по id если он существует."""
        try:
            ingredient_list_stmt = (
                (
                    select(
                        IngredientAmountModel.amount,
                        IngredientModel.id,
                        IngredientModel.measurement_unit,
                        IngredientModel.name,
                    ).filter(RecipeIngredientModel.recipe_id == id)
                )
                .outerjoin(
                    RecipeIngredientModel,
                    IngredientAmountModel.id
                    == (RecipeIngredientModel.ingredient_amount_id),
                )
                .outerjoin(
                    IngredientModel,
                    IngredientModel.id == IngredientAmountModel.ingredient_id,
                )
            )

            ingredient_list_result = await self.session.execute(ingredient_list_stmt)
            ingredient_list_result = ingredient_list_result.unique().mappings().all()
            recipe_body_stmt = (
                select(self.model)
                .filter(
                    RecipeModel.id == id,
                )
                .options(
                    selectinload(self.model.tags),
                    selectinload(self.model.author_info).load_only(
                        UserModel.username,
                        UserModel.id,
                        UserModel.first_name,
                        UserModel.last_name,
                        UserModel.email,
                    ),
                    selectinload(self.model.is_favorited),
                    selectinload(self.model.is_in_shopping_cart),
                )
            )
            recipe_body_result = await self.session.execute(recipe_body_stmt)
            recipe_body_result = recipe_body_result.scalars().one()
            recipe_image = await db.images.get_one_or_none(id=recipe_body_result.image)
            recipe_image_url = f"{MAIN_URL}{MOUNT_PATH}" f"/{recipe_image.name}"
            author_schema_response = FollowedUserRead.model_validate(
                recipe_body_result.author_info, from_attributes=True
            )
            if current_user:
                subs = await db.subscriptions.get_one_or_none(
                    author_id=recipe_body_result.author_info.id,
                    subscriber_id=current_user.id,
                )
                if subs:
                    author_schema_response.is_subscribed = True
            response = self.schema(
                id=recipe_body_result.id,
                tags=recipe_body_result.tags,
                author=author_schema_response,
                ingredients=ingredient_list_result,
                name=recipe_body_result.name,
                image=recipe_image_url,
                text=recipe_body_result.text,
                cooking_time=recipe_body_result.cooking_time,
            )
            if current_user:
                if recipe_body_result.is_favorited:
                    for elem in recipe_body_result.is_favorited:
                        if elem.user_id == current_user.id:
                            response.is_favorited = True
                if recipe_body_result.is_in_shopping_cart:
                    for elem in recipe_body_result.is_in_shopping_cart:
                        if elem.user_id == current_user.id:
                            response.is_in_shopping_cart = True
            return response
        except NoResultFound:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Рецепт не найден."
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
            while await self.check_image_name(generated_image_name):
                generated_image_name = ImageManager().create_random_name(image_base64)

            image_url = f"{MAIN_URL}{MOUNT_PATH}" f"/{generated_image_name}"
            image_id = await self.create_image(
                name=generated_image_name, base64=image_base64
            )

            _recipe_data.image = image_id
            new_obj_stmt = (
                insert(self.model)
                .values(**_recipe_data.model_dump())
                .returning(self.model)
            )
            recipe_result = await self.session.execute(new_obj_stmt)
            recipe_result = recipe_result.scalars().one()
            logger.info(
                f"Изображение {generated_image_name} для рецепта {recipe_result.id} успешно создано"
            )
            user_result = await db.users.get_one_or_none(
                user_id=recipe_result.author, current_user_id=recipe_result.id
            )
        except Exception:
            raise MainDataRecipeAtModifyingException

        ingredients_data = recipe_data.ingredients
        ingredients_result = list()
        if ingredients_data:
            try:
                _ingredients_data = await check_ingredient_duplicates_for_recipe(
                    ingredients_data=ingredients_data
                )
                ingredients_result = await db.ingredients_amount.add_recipe_ingredients(
                    ingredients_data=_ingredients_data,
                    db=db,
                    recipe_id=recipe_result.id,
                )
            except Exception:
                raise IngredientNotFoundException

        tags_data = set(recipe_data.tags)
        tags_result = list()
        if tags_data:
            try:
                tags_result = await db.recipe_tags.create(
                    tags_data=tags_data, db=db, recipe_id=recipe_result.id
                )
            except Exception:
                raise TagNotFoundException

        ImageManager().base64_to_file(
            base64_string=image_base64, image_name=generated_image_name
        )
        response = self.schema(
            name=recipe_result.name,
            text=recipe_result.text,
            cooking_time=recipe_result.cooking_time,
            author=user_result,
            id=recipe_result.id,
            tags=tags_result,
            ingredients=ingredients_result,
            image=image_url,
        )
        logger.info(f"Рецепт с id {recipe_result.id} успешно создан")
        return response

    async def update(self, db, recipe_data: RecipeUpdateRequest, id: int):
        """Обновление рецепта по его id."""
        recipe_image_id_stmt = (
            select(RecipeModel.image).filter_by(id=id).scalar_subquery()
        )
        current_image_stmt = select(ImageModel).filter(
            ImageModel.id == recipe_image_id_stmt,
        )
        file_to_delete = await self.session.execute(current_image_stmt)
        file_to_delete = file_to_delete.scalars().one()
        try:
            if recipe_data.image:
                media_path = pathlib.Path(__file__).parent.parent.resolve()
                image_to_delete = f"{media_path}{MOUNT_PATH}/{file_to_delete.name}"
                if os.path.exists(image_to_delete):
                    os.remove(image_to_delete)
                logger.info(
                    f"Изображение {file_to_delete.name} для рецета с id {id} успешно удалено"
                )
                image_base64 = recipe_data.image
                generated_image_name = ImageManager().create_random_name(image_base64)
                while await self.check_image_name(generated_image_name):
                    generated_image_name = ImageManager().create_random_name(
                        image_base64
                    )
                image_url = f"{MAIN_URL}{MOUNT_PATH}" f"/{generated_image_name}"
                image_id = await self.create_image(
                    name=generated_image_name, base64=image_base64
                )
                ImageManager().base64_to_file(
                    base64_string=image_base64, image_name=generated_image_name
                )
                logger.info(
                    f"Изображение {generated_image_name} для рецета с id {id} успешно создано"
                )
                recipe_data.image = image_id
                updated_image_stmt = (
                    update(ImageModel)
                    .filter_by(id=file_to_delete.id)
                    .values(name=generated_image_name, base64=image_base64)
                    .returning(ImageModel)
                )
                await self.session.execute(updated_image_stmt)

            else:
                image_url = f"{MAIN_URL}{MOUNT_PATH}" f"/{file_to_delete.name}"

            updated_recipe_stmt = (
                update(self.model)
                .filter_by(id=id)
                .values(
                    name=recipe_data.name,
                    text=recipe_data.text,
                    cooking_time=recipe_data.cooking_time,
                )
                .returning(self.model)
            )
            updated_recipe = await self.session.execute(updated_recipe_stmt)
            updated_recipe = updated_recipe.scalars().one()
            user_result = await db.users.get_one_or_none(
                user_id=updated_recipe.author, current_user_id=updated_recipe.id
            )
        except Exception:
            raise MainDataRecipeAtModifyingException
        ingredients_data = recipe_data.ingredients
        ingredients_result = list()
        if ingredients_data:
            try:
                _ingredients_data = await check_ingredient_duplicates_for_recipe(
                    ingredients_data=ingredients_data
                )
                ingredients_result = (
                    await db.ingredients_amount.change_recipe_ingredients(
                        ingredients_data=_ingredients_data, recipe_id=id, db=db
                    )
                )
            except Exception:
                raise IngredientNotFoundException

        tags_data = set(recipe_data.tags)
        tags_result = list()
        if tags_data:
            try:
                tags_result = await db.recipe_tags.update(
                    tags_data=tags_data, db=db, recipe_id=id
                )
            except Exception:
                raise TagNotFoundException
        response = self.schema(
            name=updated_recipe.name,
            text=updated_recipe.text,
            cooking_time=updated_recipe.cooking_time,
            author=user_result,
            id=updated_recipe.id,
            tags=tags_result,
            ingredients=ingredients_result,
            image=image_url,
        )
        logger.info(f"Рецепт с id {updated_recipe.id} успешно обновлен")
        return response

    async def delete(self, id):
        """Удаление рецепта по его id."""
        recipe_ingredient_amount_ids_stmt = select(
            RecipeIngredientModel.ingredient_amount_id
        ).filter_by(recipe_id=id)
        recipe_ingredient_amount_ids = await self.session.execute(
            recipe_ingredient_amount_ids_stmt
        )
        recipe_ingredient_amount_ids = recipe_ingredient_amount_ids.scalars().all()
        recipe_to_delete_stmt = (
            delete(self.model).filter_by(id=id).returning(self.model.image)
        )
        recipe_image_id = await self.session.execute(recipe_to_delete_stmt)
        recipe_image_id = recipe_image_id.scalars().one()
        recipe_image_to_delete_stmt = (
            delete(ImageModel).filter_by(id=recipe_image_id).returning(ImageModel.name)
        )
        image_name_to_delete = await self.session.execute(recipe_image_to_delete_stmt)
        image_name_to_delete = image_name_to_delete.scalars().one()
        media_path = pathlib.Path(__file__).parent.parent.resolve()
        image_to_delete = f"{media_path}{MOUNT_PATH}/{image_name_to_delete}"
        if os.path.exists(image_to_delete):
            os.remove(image_to_delete)
            logger.info(
                f"Изображение {image_name_to_delete} для рецета с id {id} успешно удалено"
            )
        recipe_ingredient_amount_ids_to_delete = list()
        for id in recipe_ingredient_amount_ids:
            current_obj_stmt = select(
                RecipeIngredientModel.ingredient_amount_id
            ).filter_by(ingredient_amount_id=id)
            current_obj = await self.session.execute(current_obj_stmt)
            current_obj = current_obj.scalars().one_or_none()
            if not current_obj:
                recipe_ingredient_amount_ids_to_delete.append(id)
        if recipe_ingredient_amount_ids_to_delete:
            ids_to_delete = delete(IngredientAmountModel).filter(
                IngredientAmountModel.id.in_(recipe_ingredient_amount_ids_to_delete)
            )
            await self.session.execute(ids_to_delete)
            logger.info(f"Рецепт с id {id} успешно удален")

    async def check_image_name(self, new_image_name: str):
        """Проверка уникальности названия картинки."""
        image_stmt = select(ImageModel).filter_by(name=new_image_name)
        result = await self.session.execute(image_stmt)
        return result.scalars().one_or_none()

    async def create_image(self, name, base64):
        """Создание записи в БД с данными (названием и
        исходных base64) новой картинки."""
        image_stmt = (
            insert(ImageModel)
            .values({"name": name, "base64": base64})
            .returning(ImageModel.id)
        )
        image_result = await self.session.execute(image_stmt)
        return image_result.scalars().one()

    async def check_recipe_exists(self, id: int):
        """Проверка на наличие рецепта в бд с указанным id."""
        stmt = select(self.model.author, self.model.id).filter_by(id=id)
        result = await self.session.execute(stmt)
        try:
            result = result.mappings().one()
            return CheckRecipeRead.model_validate(result, from_attributes=True)
        except NoResultFound:
            raise RecipeNotFoundException
