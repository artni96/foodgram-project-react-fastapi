from fastapi import APIRouter, Body, Depends

from backend.src.api.dependencies import DBDep, UserDep
from backend.src.repositories.utils.ingredients import \
    add_ingredients_to_recipe
from backend.src.repositories.utils.tags import recipe_tags
from backend.src.schemas.recipes import (RecipeCreate, RecipeCreateRequest,
                                         RecipeRead)
from backend.src.services.users import optional_current_user

router = APIRouter(prefix='/recipes', tags=['Рецепты',])


@router.get('/{id}')
async def get_recipe(
    db: DBDep,
    id: int,
    current_user=Depends(optional_current_user)
):
    print('Its working')
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
    recipe_data: RecipeCreateRequest = Body(
        openapi_examples=RecipeCreateRequest.Config.schema_extra['examples']
    ),
):
    _recipe_data = RecipeCreate(
        **recipe_data.model_dump(),
        author=current_user.id,
    )
    recipe = await db.recipes.create(data=_recipe_data, db=db)
    ingredients_data = recipe_data.ingredient
    if ingredients_data:
        ingredients_result = await add_ingredients_to_recipe(
            ingredients_data=ingredients_data,
            recipe_id=recipe.id,
            db=db
        )
    tags_data = recipe_data.tag
    if tags_data:
        tags_result = await recipe_tags(
            tags_data=tags_data,
            db=db,
            recipe_id=recipe.id
        )
    #     # Вынести в отдельную функцию в utils
        # recipe_tags = [RecipeTagCreate(
        #     recipe_id=recipe_id, tag_id=tag_id)
        #     for tag_id in tags_data
        # ]
        # tags_result = await db.recipe_tags.bulk_create(recipe_tags)
    response = RecipeRead(
        name=recipe.name,
        text=recipe.text,
        cooking_time=recipe.cooking_time,
        author=recipe.author,
        id=recipe.id,
        tag=tags_result,
        ingredient=ingredients_result
    )
    await db.commit()
    return response
