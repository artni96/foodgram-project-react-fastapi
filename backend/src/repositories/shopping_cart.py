from sqlalchemy import func, select

from backend.src.models.ingredients import (IngredientAmountModel,
                                            IngredientModel,
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

                IngredientModel.name,
                (
                    func.count(IngredientModel.name) *
                    IngredientAmountModel.amount
                ).label('total_amount')
            )
            .select_from(RecipeIngredientModel)
            .group_by(IngredientModel.id, IngredientAmountModel.amount)
            .filter(self.model.user_id == user_id)

            .join(
                self.model,
                RecipeIngredientModel.recipe_id == self.model.recipe_id
            )
            .join(
                IngredientAmountModel,
                IngredientAmountModel.id == (
                    RecipeIngredientModel.ingredient_amount_id
                )
            )
            .join(
                IngredientModel,
                IngredientModel.id == IngredientAmountModel.ingredient_id
            )

        )
        product_list = await self.session.execute(
            user_product_list_stmt
        )
        return product_list.mappings().all()
