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
    _recipe_data = RecipeCreate(
        **recipe_data.model_dump(),
        author=current_user.id,
    )
    recipe = await db.recipes.create(data=_recipe_data, db=db)
    ingredients_data = recipe_data.ingredient
    if ingredients_data:
        _ingredients_data = await check_ingredient_duplicates_for_recipe(
            ingredients_data=ingredients_data
        )
        ingredients_result = (
            await db.ingredients_amount.add_recipe_ingredients(
                ingredients_data=_ingredients_data,
                db=db,
                recipe_id=recipe.id
            )
        )
    tags_data = recipe_data.tag
    if tags_data:

        tags_result = await db.recipe_tags.create(
            tags_data=tags_data,
            db=db,
            recipe_id=recipe.id
        )
    response = RecipeRead(
        name=recipe.name,
        text=recipe.text,
        cooking_time=recipe.cooking_time,
        author=recipe.author,
        id=recipe.id,
        tag=tags_result,
        ingredient=ingredients_result,
        image=recipe.image
    )
    await db.commit()
    return response


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
        try:
            _recipe_data = RecipeUpdate(
                **recipe_data.model_dump(),
                id=id
            )
            recipe = await db.recipes.update(data=_recipe_data, db=db)
            ingredients_data = recipe_data.ingredient
            if ingredients_data:

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
            tags_data = recipe_data.tag
            if tags_data:
                tags_result = await create_recipe_tags(
                    tags_data=tags_data,
                    db=db,
                    recipe_id=recipe.id
                )
            response = RecipeRead(
                name=recipe.name,
                text=recipe.text,
                cooking_time=recipe.cooking_time,
                author=recipe.author,
                id=recipe.id,
                tag=tags_result,
                ingredient=ingredients_result,
                image=recipe.image
            )
            await db.commit()
            return response
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Не удалось создать рецепт'
                )
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail='Редакция рецепта доступна только его автору.'
    )
