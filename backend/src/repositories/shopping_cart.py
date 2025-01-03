from fastapi.responses import FileResponse
from sqlalchemy import func, select, delete
from sqlalchemy.exc import NoResultFound

from backend.src.models.ingredients import (
    IngredientAmountModel,
    IngredientModel,
    RecipeIngredientModel,
)
from backend.src.models.recipes import ShoppingCartModel
from backend.src.models.users import UserModel
from backend.src.repositories.favorite_recipes import FavoriteRecipeRepository
from backend.src.schemas.recipes import ShoppingCartRecipeRead
from backend.src.utils.pdf_shopping_list import create_shopping_list


class ShoppingCartRepository(FavoriteRecipeRepository):
    model = ShoppingCartModel
    schema = ShoppingCartRecipeRead

    async def get_shopping_cart(self, user_id):
        """Ответ со списком покупок в формате pdf."""
        user_product_list_stmt = (
            select(
                IngredientModel.name,
                (func.count(IngredientModel.name) * IngredientAmountModel.amount).label(
                    "total_amount"
                ),
                IngredientModel.measurement_unit,
            )
            .select_from(RecipeIngredientModel)
            .group_by(IngredientModel.id, IngredientAmountModel.amount)
            .filter(self.model.user_id == user_id)
            .join(self.model, RecipeIngredientModel.recipe_id == self.model.recipe_id)
            .join(
                IngredientAmountModel,
                IngredientAmountModel.id
                == (RecipeIngredientModel.ingredient_amount_id),
            )
            .join(
                IngredientModel,
                IngredientModel.id == IngredientAmountModel.ingredient_id,
            )
        )
        username_stmt = select(UserModel.username).filter_by(id=user_id)
        username = await self.session.execute(username_stmt)
        username = username.scalars().one()
        product_list = await self.session.execute(user_product_list_stmt)
        result_list = [
            f'{elem["name"].capitalize()} - {elem["total_amount"]} {elem["measurement_unit"]}'
            for elem in product_list.mappings().all()
        ]
        pdf_file = create_shopping_list(data=result_list, username=username)
        return FileResponse(
            path=pdf_file,
            media_type="multipart/form-data",
            headers={
                "Content-Type": "application/pdf",
                "Content-Disposition": f'attachment; filename={pdf_file.split("/")[-1]}',
            },
        )

    async def delete(self, **filter_by):
        """Удаление рецепта из списка покупок."""
        stmt = delete(self.model).filter_by(**filter_by).returning(self.model)
        sub_to_delete = await self.session.execute(stmt)
        try:
            return sub_to_delete.scalars().one()
        except NoResultFound:
            raise NoResultFound
