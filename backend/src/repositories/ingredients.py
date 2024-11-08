from sqlalchemy import delete, select

from backend.src.base import (IngredientAmountModel, IngredientModel,
                              RecipeIngredientModel)
from backend.src.repositories.base import BaseRepository
from backend.src.schemas.ingredients import (IngredientAmountCreate,
                                             IngredientAmountRead,
                                             IngredientRead,
                                             RecipeIngredientAmountCreate,
                                             RecipeIngredientAmountRead)


class IngredientRepository(BaseRepository):
    model = IngredientModel
    schema = IngredientRead

    async def get_filtered(self, name: str | None):
        filtered_ingredients_stmt = select(self.model)
        if name:
            filtered_ingredients_stmt = (
                filtered_ingredients_stmt.filter(
                    self.model.name.startswith(name.lower())
                )
            )
        filtered_ingredients = await self.session.execute(
            filtered_ingredients_stmt
        )
        filtered_ingredients = filtered_ingredients.scalars().all()
        return [
            self.schema.model_validate(obj, from_attributes=True)
            for obj in filtered_ingredients
        ]


class IngredientAmountRepository(BaseRepository):
    model = IngredientAmountModel
    schema = IngredientAmountRead

    async def add_recipe_ingredients(self, ingredients_data, recipe_id, db):
        ingredients_amount_list_to_create: list[IngredientAmountCreate] = (
            list()
        )
        existing_ingredients_amount_ids: list[int] = list()
        ingredients_amount_list_response: list[RecipeIngredientAmountRead] = (
            list()
        )
        for obj in ingredients_data:
            current_ingredient_amount = (
                await db.ingredients_amount.get_one_or_none(
                    ingredient_id=obj.ingredient_id,
                    amount=obj.amount)
            )
            if current_ingredient_amount:
                existing_ingredients_amount_ids.append(
                    current_ingredient_amount.id)
            else:
                ingredients_amount_list_to_create.append(
                    IngredientAmountCreate(
                        ingredient_id=obj.ingredient_id,
                        amount=obj.amount
                    )
                )
            current_ingredient = await db.ingredients.get_one_or_none(
                id=obj.ingredient_id
            )
            ingredients_amount_list_response.append(
                RecipeIngredientAmountRead(
                    id=current_ingredient.id,
                    name=current_ingredient.name,
                    measurement_unit=current_ingredient.measurement_unit,
                    amount=obj.amount
                )
            )
        if ingredients_amount_list_to_create:
            ingredients_amount_ids = await db.ingredients_amount.bulk_create(
                ingredients_amount_list_to_create
            )
            ingredients_amount_ids += existing_ingredients_amount_ids
        else:
            ingredients_amount_ids = existing_ingredients_amount_ids
        recipe_ingredients_amount_data = [
            RecipeIngredientAmountCreate(
                recipe_id=recipe_id,
                ingredient_amount_id=_id)
            for _id in ingredients_amount_ids
        ]
        await db.recipe_ingredient_amount.bulk_create(
            recipe_ingredients_amount_data
        )
        return ingredients_amount_list_response

    async def change_recipe_ingredients(self, ingredients_data, recipe_id, db):
        ingredients_amount_stmt = (
            select(RecipeIngredientModel.ingredient_amount_id)
            .filter_by(recipe_id=recipe_id)
            .subquery('ingredients_amount_stmt')
        )
        current_ingredient_ids_stmt = (
            select(
                IngredientAmountModel.id,
                IngredientAmountModel.ingredient_id
            )
            .filter(IngredientAmountModel.id.in_(ingredients_amount_stmt))
        )
        current_ingredients = await self.session.execute(
            current_ingredient_ids_stmt
        )
        current_ingredients = current_ingredients.mappings().all()
        current_ingredient_amount_ids = [obj.id for obj in current_ingredients]
        ingredients_to_del_stmt = (
            delete(IngredientAmountModel)
            .filter(IngredientAmountModel.id.in_(current_ingredient_amount_ids))
        )
        await self.session.execute(ingredients_to_del_stmt)
        new_ingredients = await self.add_recipe_ingredients(
            ingredients_data=ingredients_data,
            recipe_id=recipe_id,
            db=db
        )
        return new_ingredients


class RecipeIngredientAmountRepository(BaseRepository):
    model = RecipeIngredientModel
