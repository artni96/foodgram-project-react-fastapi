from sqlalchemy import insert, select, delete

from backend.src.constants import MAIN_URL, MOUNT_PATH
from backend.src.models.recipes import (FavoriteRecipeModel, ImageModel,
                                        RecipeModel)
from backend.src.repositories.base import BaseRepository
from backend.src.schemas.recipes import FavoriteRecipeRead


class FavoriteRecipeRepository(BaseRepository):
    model = FavoriteRecipeModel
    schema = FavoriteRecipeRead

    async def create(self, data):
        # favorite_recipe_info_stmt = (
        #     select(
        #         RecipeModel.id,
        #         RecipeModel.name,
        #         RecipeModel.cooking_time,
        #         ImageModel.name.label('image')
        #     )
        #     .join(ImageModel, ImageModel.id == RecipeModel.image)
        #     .filter_by(id=data.recipe_id)
        # )
        make_recipe_favorite_stmt = (
            insert(self.model)
            .values(**data.model_dump())
            .returning(self.model.recipe_id)
        )
        favorite_recipe_id = await self.session.execute(
            make_recipe_favorite_stmt
        )
        favorite_recipe_id = favorite_recipe_id.scalars().one()
        favorite_recipe_info_stmt = (
            select(
                RecipeModel.id,
                RecipeModel.name,
                RecipeModel.cooking_time,
                ImageModel.name.label('image')
            )
            .join(ImageModel, ImageModel.id == RecipeModel.image)
            .filter(RecipeModel.id == favorite_recipe_id)
        )
        favorite_recipe_info = await self.session.execute(
            favorite_recipe_info_stmt
        )
        favorite_recipe_info = favorite_recipe_info.mappings().one()
        image_url = f'{MAIN_URL}{MOUNT_PATH}/{favorite_recipe_info.image}'
        return self.schema(
            id=favorite_recipe_info.id,
            name=favorite_recipe_info.name,
            image=image_url,
            cooking_time=favorite_recipe_info.cooking_time
        )

    async def delete(self, **filter_by):
        stmt = delete(self.model).filter_by(**filter_by).returning(self.model.id)
        result = await self.session.execute(stmt)
        result = result.scalars().one_or_none()
        return result
