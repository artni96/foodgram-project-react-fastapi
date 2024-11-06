from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy import insert, select
from sqlalchemy.orm import selectinload

from backend.src.models.recipes import RecipeModel
from backend.src.repositories.base import BaseRepository
from backend.src.schemas.recipes import RecipeAfterCreateRead, RecipeCreate
from backend.src.utils.image_manager import ImageManager
from backend.src.constants import DOMAIN_ADDRESS, MOUNT_PATH


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

    async def create(self, data: RecipeCreate, db):
        # try:
            generated_image_name = ImageManager().create_random_name()
            while await self.check_image_name(generated_image_name):
                generated_image_name = ImageManager().create_random_name()
            image_base64 = data.image
            data.image = generated_image_name
            new_obj_stmt = (
                insert(self.model)
                .values(**data.model_dump())
                .returning(self.model)
            )
            recipe_result = await self.session.execute(new_obj_stmt)
            recipe_result = recipe_result.scalars().one()
            # image_base64 = data.image
            user_result = await db.users.get_one_or_none(
                user_id=recipe_result.author,
                current_user_id=recipe_result.id
            )
            if recipe_result:
                ImageManager().base64_to_file(
                    base64_string=image_base64,
                    image_name=generated_image_name)
                return self.schema(
                    author=user_result,
                    name=recipe_result.name,
                    text=recipe_result.text,
                    cooking_time=recipe_result.cooking_time,
                    id=recipe_result.id,
                    image=f'{DOMAIN_ADDRESS}{MOUNT_PATH}/{generated_image_name}'
                )
        # except Exception:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail='не удалось создать рецепт с предоставленными данными'
        #     )

    async def check_image_name(self, created_image):
        image_stmt = select(self.model).filter_by(image=created_image)
        result = await self.session.execute(image_stmt)
        return result.scalars().one_or_none()