from fastapi import APIRouter, Body, Depends, HTTPException, status

from backend.src.api.dependencies import DBDep, UserDep
from backend.src.schemas.recipes import (RecipeCreateRequest,
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


@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    summary='Создание рецепта',
    description='Доступно только авторизованному пользователю'
)
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


@router.patch(
    '/{id}',
    status_code=status.HTTP_200_OK,
    summary='Обновление рецепта',
    description='Доступно только автору данного рецепта'
)
async def update_recipe(
    db: DBDep,
    current_user: UserDep,
    id: int,
    recipe_data: RecipeUpdateRequest = Body(
        openapi_examples=RecipeUpdateRequest.Config.schema_extra['examples']
    ),
):
    check_recipe = await db.recipes.check_recipe_exists(id=id)
    if check_recipe:
        if check_recipe.author == current_user.id:
            recipe = await db.recipes.update(
                recipe_data=recipe_data,
                id=id,
                db=db
            )
            await db.commit()
            return recipe
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Редакция рецепта доступна только его автору.'
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Рецепт с указанным id не найден.'
        )


@router.delete(
    '/{id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Удаление рецепта',
    description='Доступно только автору данного рецепта'
    )
async def delete_recipe(
    db: DBDep,
    current_user: UserDep,
    id: int
):
    check_recipe = await db.recipes.check_recipe_exists(id=id)
    if check_recipe:
        if check_recipe.author == current_user.id:
            recipe = await db.recipes.delete(id=id)
            await db.commit()
            return recipe
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Редакция рецепта доступна только его автору.'
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Рецепт с указанным id не найден.'
        )
