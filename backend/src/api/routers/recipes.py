from fastapi import APIRouter, Body, Depends, HTTPException, status

from backend.src.api.dependencies import DBDep, UserDep
from backend.src.repositories.utils.ingredients import \
    check_ingredient_duplicates_for_recipe
from backend.src.repositories.utils.tags import create_recipe_tags
from backend.src.schemas.recipes import (RecipeCreate, RecipeCreateRequest,
                                         RecipeRead, RecipeUpdate,
                                         RecipeUpdateRequest)
from backend.src.services.users import optional_current_user

router = APIRouter(prefix='/api/recipes', tags=['Рецепты',])


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
    recipe = await db.recipes.create(
        recipe_data=recipe_data,
        current_user=current_user,
        db=db
    )
    await db.commit()
    return recipe


@router.patch('/{id}')
async def update_recipe(
    db: DBDep,
    current_user: UserDep,
    id: int,
    recipe_data: RecipeUpdateRequest = Body(
        openapi_examples=RecipeUpdateRequest.Config.schema_extra['examples']
    ),
):
    if await db.recipes.check_user_is_author(id=id, author=current_user.id):
        recipe = await db.recipes.update(recipe_data=recipe_data, id=id, db=db)
        await db.commit()
        return recipe
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail='Редакция рецепта доступна только его автору.'
    )
