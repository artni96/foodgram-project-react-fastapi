import os
import pathlib

from fastapi import HTTPException, status
from sqlalchemy import delete, insert, select, update, func, and_

from backend.src.constants import DOMAIN_ADDRESS, MOUNT_PATH
from backend.src.models.ingredients import (IngredientAmountModel,
                                            IngredientModel,
                                            RecipeIngredientModel)
from backend.src.models.recipes import (FavoriteRecipeModel, ImageModel,
                                        RecipeModel, ShoppingCartModel)
from backend.src.models.tags import RecipeTagModel, TagModel
from backend.src.models.users import UserModel
from backend.src.repositories.base import BaseRepository
from backend.src.repositories.utils.ingredients import \
    check_ingredient_duplicates_for_recipe
from backend.src.schemas.recipes import (CheckRecipeRead, ImageRead,
                                         RecipeCreate, RecipeCreateRequest,
                                         RecipeRead, RecipeUpdate,
                                         RecipeUpdateRequest)
from backend.src.schemas.users import FollowedUserRead
from backend.src.utils.image_manager import ImageManager
from backend.src.models.subscriptions import SubscriptionModel


class ImageRepository(BaseRepository):
    model = ImageModel
    schema = ImageRead


class RecipeRepository(BaseRepository):
    model = RecipeModel
    schema = RecipeRead

    async def test_list(
            self,
            current_user,
            is_favorite,
            is_in_shopping_cart
    ):
        base_recipe_list_stmt = (
            select(
                self.model.text,
                self.model.id,
                UserModel.username,
                UserModel.email,
                UserModel.id,
                UserModel.first_name,
                UserModel.last_name,
                SubscriptionModel.id.label('is_subscribed'),
                TagModel.id,
                TagModel.name,
                TagModel.color,
                TagModel.slug
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
            .outerjoin(
                RecipeTagModel,
                RecipeTagModel.recipe_id == self.model.id
            )
            .outerjoin(
                TagModel,
                TagModel.id == RecipeTagModel.tag_id
            )
        )
        if is_favorite:
            base_recipe_list_stmt = base_recipe_list_stmt.join(
                FavoriteRecipeModel,
                FavoriteRecipeModel.recipe_id == self.model.id
            )
        if is_in_shopping_cart:
            base_recipe_list_stmt = base_recipe_list_stmt.join(
                ShoppingCartModel,
                ShoppingCartModel.recipe_id == self.model.id
            )
        recipe_list = await self.session.execute(base_recipe_list_stmt)
        result = recipe_list.mappings().all()
        return result

    async def get_one_or_none(self, id, current_user, db):
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
        tag_list_stmt = (
            select(TagModel.id, TagModel.name, TagModel.slug, TagModel.color)
            .join(RecipeTagModel, RecipeTagModel.tag_id == TagModel.id)
            .filter(RecipeTagModel.recipe_id == id)
        )
        tag_list_result = await self.session.execute(
            tag_list_stmt
        )
        tag_list_result = (
            tag_list_result.unique().mappings().all()
        )
        recipe_body_stmt = (
            select(RecipeModel)
            .filter_by(id=id)
        )
        recipe_body_result = await self.session.execute(recipe_body_stmt)
        recipe_body_result = recipe_body_result.scalars().one()
        recipe_image = await db.images.get_one_or_none(
            id=recipe_body_result.image
        )
        recipe_image_url = (
                f'{DOMAIN_ADDRESS}{MOUNT_PATH}'
                f'/{recipe_image.name}'
            )
        author_stmt = (
            select(
                UserModel.email,
                UserModel.id,
                UserModel.username,
                UserModel.first_name,
                UserModel.last_name
            )
            .filter_by(id=recipe_body_result.author)
        )
        author_result = await self.session.execute(author_stmt)
        author_result = author_result.mappings().one()
        author_schema_response = FollowedUserRead(
            email=author_result.email,
            username=author_result.username,
            first_name=author_result.first_name,
            last_name=author_result.last_name,
            id=author_result.id
        )
        if current_user:
            if current_user.id == author_result.id:
                author_schema_response.is_subscribed = False
            else:
                subs = await db.subscriptions.get_one_or_none(
                    author_id=author_result.id,
                    subscriber_id=current_user.id
                )
                if not subs:
                    author_schema_response.is_subscribed = False
        else:
            author_schema_response.is_subscribed = False
        response = self.schema(
            id=recipe_body_result.id,
            tags=tag_list_result,
            author=author_schema_response,
            ingredients=ingredient_list_result,
            name=recipe_body_result.name,
            image=recipe_image_url,
            text=recipe_body_result.text,
            cooking_time=recipe_body_result.cooking_time
        )
        return response

    async def create(self, recipe_data: RecipeCreateRequest, db, current_user):
        '''Создание нового рецепта.'''
        _recipe_data = RecipeCreate(
            **recipe_data.model_dump(),
            author=current_user.id,
        )
        try:
            generated_image_name = ImageManager().create_random_name()
            while await self.check_image_name(generated_image_name):
                generated_image_name = ImageManager().create_random_name()
            image_base64 = _recipe_data.image
            image_name = ImageManager().base64_to_file(
                base64_string=image_base64,
                image_name=generated_image_name)
            image_url = (
                f'{DOMAIN_ADDRESS}{MOUNT_PATH}'
                f'/{image_name}'
            )
            image_id = await self.create_image(
                name=image_name,
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
        ingredients_data = recipe_data.ingredient
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
        tags_data = recipe_data.tag
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
        response = self.schema(
            name=recipe_result.name,
            text=recipe_result.text,
            cooking_time=recipe_result.cooking_time,
            author=user_result,
            id=recipe_result.id,
            tag=tags_result,
            ingredient=ingredients_result,
            image=image_url
        )
        return response

    async def update(self, recipe_data: RecipeUpdateRequest, db, id):
        _recipe_data = RecipeUpdate(
            **recipe_data.model_dump(),
            id=id
        )
        try:
            recipe_image_id_stmt = (
                select(RecipeModel.image)
                .filter_by(id=_recipe_data.id)
                .subquery('recipe_image_id')
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
                print(image_to_delete)
                if os.path.exists(image_to_delete):
                    os.remove(image_to_delete)
                image_base64 = _recipe_data.image
                _recipe_data.image = current_image.id
                image_name = ImageManager().base64_to_file(
                    base64_string=image_base64,
                    image_name=current_image.name.split('.')[0])

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
        ingredients_data = recipe_data.ingredient
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

        tags_data = recipe_data.tag
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
            tag=tags_result,
            ingredient=ingredients_result,
            image=image_url
        )
        return response

    async def delete(self, id):
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
        print(recipe_ingredient_amount_ids)
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
        print(image_to_delete)
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

    async def check_image_name(self, new_image_name):
        '''Проверка уникальности названия картинки.'''
        image_stmt = select(ImageModel).filter_by(name=new_image_name)
        result = await self.session.execute(image_stmt)
        return result.scalars().one_or_none()

    async def create_image(self, name, base64):
        '''Создание записи в БД с данными (названием и
         исходных base64) новой картинки.'''
        image_stmt = insert(ImageModel).values(
            {'name': name, 'base64': base64}
        ).returning(ImageModel.id)
        image_result = await self.session.execute(image_stmt)
        return image_result.scalars().one()

    async def check_recipe_exists(self, id):
        stmt = select(self.model.author, self.model.id).filter_by(id=id)
        result = await self.session.execute(stmt)
        result = result.mappings().one_or_none()
        if result:
            return CheckRecipeRead.model_validate(result, from_attributes=True)
