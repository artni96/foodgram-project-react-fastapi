from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.src.models.ingredients import (IngredientAmountModel, IngredientModel,
                                            RecipeIngredientModel)
from backend.src.models.recipes import ShoppingCartModel
from backend.src.repositories.favorite_recipes import FavoriteRecipeRepository
from backend.src.schemas.recipes import ShoppingCartRecipeRead


class ShoppingCartRepository(FavoriteRecipeRepository):
    model = ShoppingCartModel
    schema = ShoppingCartRecipeRead

    async def get_shopping_cart(self, user_id):
        user_product_list_stmt = (
            select(
                self.model.id,
                RecipeIngredientModel.recipe_id,
                IngredientModel.name,
                IngredientAmountModel.amount,
            )
            .filter_by(user_id=user_id)
            .outerjoin(
                RecipeIngredientModel,
                RecipeIngredientModel.recipe_id == self.model.recipe_id
            )
            .outerjoin(
                IngredientAmountModel,
                IngredientAmountModel.id == RecipeIngredientModel.ingredient_amount_id
            )
            .outerjoin(
                IngredientModel,
                IngredientModel.id == IngredientAmountModel.ingredient_id
            )
        )
        product_list = await self.session.execute(
            user_product_list_stmt
        )
        return product_list.mappings().all()
