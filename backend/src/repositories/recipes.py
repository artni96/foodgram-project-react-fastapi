import os
import pathlib

from fastapi import HTTPException, status
from sqlalchemy import insert, select, update
from sqlalchemy.orm import selectinload

from backend.src.constants import DOMAIN_ADDRESS, MOUNT_PATH
from backend.src.models.recipes import ImageModel, RecipeModel
from backend.src.repositories.base import BaseRepository
from backend.src.repositories.utils.ingredients import \
    check_ingredient_duplicates_for_recipe
from backend.src.repositories.utils.tags import create_recipe_tags
from backend.src.schemas.recipes import (RecipeAfterCreateRead, RecipeCreate,
                                         RecipeCreateRequest, RecipeRead,
                                         RecipeUpdate, RecipeUpdateRequest)
from backend.src.utils.image_manager import ImageManager


class RecipeRepository(BaseRepository):
    model = RecipeModel
    schema = RecipeAfterCreateRead

    async def get_one_or_none(self, recipe_id, current_user_id, db):
        recipe_stmt = (
            select(self.model)
            .filter_by(id=recipe_id)
            .options(selectinload(self.model.tag))
        )

        recipe_result = await self.session.execute(recipe_stmt)
        recipe_result = recipe_result.scalars().one_or_none()
        user_result = await db.users.get_one_or_none(
            user_id=recipe_result.author,
            current_user_id=current_user_id
        )
        if recipe_result:
            return self.schema(
                author=user_result,
                name=recipe_result.name,
                text=recipe_result.text,
                cooking_time=recipe_result.cooking_time,
                tag=recipe_result.tag,
                id=recipe_result.id
            )

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
        response = RecipeRead(
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
                tags_result = await create_recipe_tags(
                    tags_data=tags_data,
                    db=db,
                    recipe_id=id
                )
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='Указанных тегов нет в БД.'
                )
        response = RecipeRead(
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

    async def check_user_is_author(self, author, id):
        stmt = select(self.model).filter_by(id=id, author=author)
        result = await self.session.execute(stmt)
        result = result.scalars().one_or_none()
        return result
