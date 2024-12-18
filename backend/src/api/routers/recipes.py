import re

from fastapi import APIRouter, Body, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError, NoResultFound

from backend.src import constants
from backend.src.api.dependencies import DBDep, UserDep, OptionalUserDep
from backend.src.exceptions.ingredients import IngredientNotFoundException
from backend.src.exceptions.recipes import MainDataRecipeAtModifyingException, RecipeNotFoundException
from backend.src.exceptions.tags import TagNotFoundException
from backend.src.schemas.recipes import (FavoriteRecipeCreate,
                                         RecipeCreateRequest,
                                         RecipeUpdateRequest,
                                         ShoppingCartRecipeCreate, RecipeRead, RecipeListRead, FavoriteRecipeRead,
                                         ShoppingCartRecipeRead)


ROUTER_PREFIX = '/api/recipes'
recipe_router = APIRouter(prefix=ROUTER_PREFIX, tags=['Рецепты', ])



@recipe_router.get(
    '',
    status_code=status.HTTP_200_OK,
    summary='Список рецептов',
    description=(
            'Страница доступна всем пользователям. Доступна фильтрация по '
            'избранному, автору, списку покупок и тегам.'
    )
)
async def get_recipe_list(
    db: DBDep,
    current_user: OptionalUserDep,
    author: int | None = Query(default=None),
    tags: list[str] | None = Query(default=None),
    is_favorited: int = Query(default=0),
    is_in_shopping_cart: int = Query(default=0),
    page: int | None = Query(default=None, title='Номер страницы'),
    limit: int | None = Query(
        default=None,
        title='Количество объектов на странице.'
    ),
) -> RecipeListRead | None:
    if not limit:
        limit = constants.PAGINATION_LIMIT
    if not page:
        page = 1
    result = await db.recipes.get_filtered(
        current_user=current_user,
        is_favorited=is_favorited,
        is_in_shopping_cart=is_in_shopping_cart,
        tags=tags,
        author=author,
        db=db,
        limit=limit,
        page=page,
        router_prefix=ROUTER_PREFIX,
    )
    return result


@recipe_router.get(
    '/{id}',
    status_code=status.HTTP_200_OK,
    summary='Получение рецепта'
)
async def get_recipe(
    db: DBDep,
    id: int,
    current_user: OptionalUserDep
) -> RecipeRead | None:
    result = await db.recipes.get_one_or_none(
        id=id,
        current_user=current_user,
        db=db
    )
    return result


@recipe_router.post(
    '',
    status_code=status.HTTP_201_CREATED,
    summary='Создание рецепта',
    description='Доступно только авторизованному пользователю'
)
async def create_recipe(
    db: DBDep,
    current_user: UserDep,
    recipe_data: RecipeCreateRequest = Body(
        openapi_examples=RecipeCreateRequest.model_config['json_schema_extra']
    ),
):
    try:
        recipe = await db.recipes.create(
            recipe_data=recipe_data,
            current_user_id=current_user.id,
            db=db
        )
        await db.commit()
        return recipe

    except MainDataRecipeAtModifyingException as ex:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ex.detail
        )
    except TagNotFoundException as ex:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ex.detail
        )
    except IngredientNotFoundException as ex:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ex.detail
        )

@recipe_router.patch(
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
        openapi_examples=RecipeUpdateRequest.model_config['json_schema_extra']
    ),
) -> RecipeRead:
    try:
        check_recipe = await db.recipes.check_recipe_exists(id=id)
    # if check_recipe:
        if check_recipe.author == current_user.id:
            try:
                recipe = await db.recipes.update(
                    recipe_data=recipe_data,
                    id=id,
                    db=db
                )
                await db.commit()
                return recipe
            except MainDataRecipeAtModifyingException as ex:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ex.detail
                )
            except TagNotFoundException as ex:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ex.detail
                )
            except IngredientNotFoundException as ex:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ex.detail
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Редактирование рецепта доступна только его автору.'
            )
    except RecipeNotFoundException as ex:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ex.detail
        )


@recipe_router.delete(
    '/{id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Удаление рецепта',
    description='Доступно только автору данного рецепта'
)
async def delete_recipe(
        db: DBDep,
        current_user: UserDep,
        id: int
) -> None:

    try:
        check_recipe = await db.recipes.check_recipe_exists(id=id)
        if check_recipe.author == current_user.id:
            recipe = await db.recipes.delete(id=id)
            await db.commit()
            return recipe
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Редактирование рецепта доступна только его автору.'
            )
    except RecipeNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Рецепт с указанным id не найден.'
        )


favorite_recipe_router = APIRouter(
    prefix=ROUTER_PREFIX,
    tags=['Избранное', ]
)


@favorite_recipe_router.post(
    '/{id}/favorite',
    summary='Добавить рецепт в избранное',
    description='Доступно только авторизованному пользователю',
    status_code=status.HTTP_201_CREATED
)
async def make_recipe_favorite(
    id: int,
    db: DBDep,
    current_user: UserDep,
) -> FavoriteRecipeRead:
    favorite_recipe_data = FavoriteRecipeCreate(
        recipe_id=id,
        user_id=current_user.id
    )
    try:
        result = await db.favorite_recipes.create(data=favorite_recipe_data)
        await db.commit()
    except IntegrityError as e:
        error_pattern = r'Ключ \(recipe_id\)=\(\d+\) отсутствует в таблице "recipe"'
        if re.findall(error_pattern, str(e.__cause__).split('DETAIL:')[1]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Рецепт c id {id} не найден.'
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Рецепт уже в избранном.'
        )
    return result


@favorite_recipe_router.delete(
    '/{id}/favorite',
    summary='Удалить рецепт из избранного',
    description='Доступно только авторизованным пользователям',
    status_code=status.HTTP_204_NO_CONTENT
)
async def cancel_favorite_recipe(
    id: int,
    db: DBDep,
    current_user: UserDep,
) -> None:
    try:
        await db.favorite_recipes.delete(recipe_id=id, user_id=current_user.id)
        await db.commit()

    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Рецепт с id {id} в избранном не найден.'
        )


shopping_cart_router = APIRouter(
    prefix=ROUTER_PREFIX,
    tags=['Список покупок', ]
)


@shopping_cart_router.get(
    '/download_shopping_cart',
    status_code=status.HTTP_200_OK,
    summary='Скачать список покупок',
    description='Скачать файл со списком покупок.'
)
async def download_shopping_cart(
    db: DBDep,
    current_user: UserDep
):
    get_shopping_cart = await db.shopping_cart.get_shopping_cart(
        user_id=current_user.id
    )
    return get_shopping_cart


@shopping_cart_router.post(
    '/{id}/shopping_cart',
    summary='Добавить рецепт в список покупок',
    description='Доступно только авторизованным пользователям',
    status_code=status.HTTP_201_CREATED
)
async def add_recipe_to_shopping_cart(
    id: int,
    db: DBDep,
    current_user: UserDep,
) -> ShoppingCartRecipeRead:
    shopping_cart_recipe_data = ShoppingCartRecipeCreate(
        recipe_id=id,
        user_id=current_user.id
    )
    try:
        result = await db.shopping_cart.create(data=shopping_cart_recipe_data)
        await db.commit()
    except IntegrityError as e:
        error_pattern = r'Ключ \(recipe_id\)=\(\d+\) отсутствует в таблице "recipe"'
        if re.findall(error_pattern, str(e.__cause__).split('DETAIL:')[1]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Рецепт c id {id} не найден.'
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Рецепт уже в списке покупок.'
        )
    return result


@shopping_cart_router.delete(
    '/{id}/shopping_cart',
    summary='Удалить рецепт из списка покупок',
    description='Доступно только авторизованным пользователям',
    status_code=status.HTTP_204_NO_CONTENT
)
async def remove_recipe_from_shopping_cart(
    id: int,
    db: DBDep,
    current_user: UserDep,
) -> None:
    try:
        await db.shopping_cart.delete(recipe_id=id, user_id=current_user.id)
        await db.commit()

    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Рецепт в списке покупок не найден.'
        )
