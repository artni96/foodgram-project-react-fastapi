from fastapi import APIRouter

from backend.src.api.dependencies import DBDep, UserDep
from backend.src.schemas.ingredients import (IngredientAmountCreate,
                                             RecipeIngredientAmountCreate)
from backend.src.schemas.recipes import RecipeCreate, RecipeCreateRequest
from backend.src.schemas.tags import RecipeTagCreate
from backend.src.repositories.utils.ingredients import add_ingredients_to_recipe

router = APIRouter(prefix='/recipes', tags=['Рецепты',])


@router.get('/{id}')
async def get_recipe(
    db: DBDep,
    id: int,
    current_user: UserDep
):
    result = await db.recipes.get_one_or_none(
        recipe_id=id,
        current_user_id=current_user.id,
        db=db
    )
    return result


@router.post('/')
async def create_recipe(
    db: DBDep,
    current_user: UserDep,
    recipe_data: RecipeCreateRequest,
):
    _recipe_data = RecipeCreate(
        **recipe_data.model_dump(),
        author=current_user.id,
    )
    recipe_id = await db.recipes.create(data=_recipe_data)
    ingredients_data = recipe_data.ingredient
    if ingredients_data:
        ingredients_amount_list_response = await add_ingredients_to_recipe(
            ingredients_data=ingredients_data,
            recipe_id=recipe_id,
            db=db
        )
    tags_data = recipe_data.tag
    if tags_data:
        recipe_tags = [RecipeTagCreate(
            recipe_id=recipe_id, tag_id=tag_id)
            for tag_id in tags_data
        ]
        tags_result = await db.recipe_tags.bulk_create(recipe_tags)
    await db.commit()

    return {'status': 'OK'}
