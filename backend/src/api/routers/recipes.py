from fastapi import APIRouter, Body, HTTPException, Query, status
from loguru import logger
from starlette.requests import Request
from starlette.status import HTTP_400_BAD_REQUEST

from backend.src import constants
from backend.src.api.dependencies import DBDep, UserDep, OptionalUserDep
from backend.src.exceptions.ingredients import IngredientNotFoundException
from backend.src.exceptions.recipes import (
    MainDataRecipeAtModifyingException,
    RecipeNotFoundException,
    OnlyAuthorCanEditRecipeException,
    RecipeAlreadyIsInShoppingListException,
    RecipeAlreadyIsFavoritedException,
    RecipeNotInShoppingListException,
    RecipeNotFavoritedException,
)
from backend.src.exceptions.tags import TagNotFoundException
from backend.src.logs.foodgram_logger import api_success_log, api_exception_log
from backend.src.schemas.recipes import (
    RecipeCreateRequest,
    RecipeUpdateRequest,
    RecipeRead,
    RecipeListRead,
    FavoriteRecipeRead,
    ShoppingCartRecipeRead,
)
from backend.src.services.recipes import RecipeService

ROUTER_PREFIX = "/api/recipes"
recipe_router = APIRouter(
    prefix=ROUTER_PREFIX,
    tags=[
        "Рецепты",
    ],
)


@recipe_router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="Список рецептов",
    description=(
        "Страница доступна всем пользователям. Доступна фильтрация по "
        "избранному, автору, списку покупок и тегам."
    ),
)
async def get_recipe_list(
    request: Request,
    db: DBDep,
    current_user: OptionalUserDep,
    author: int | None = Query(default=None),
    tags: list[str] | None = Query(default=None),
    is_favorited: int = Query(default=0),
    is_in_shopping_cart: int = Query(default=0),
    page: int | None = Query(default=None, title="Номер страницы"),
    limit: int | None = Query(default=None, title="Количество объектов на странице."),
) -> RecipeListRead | None:
    if not limit:
        limit = constants.PAGINATION_LIMIT
    if not page:
        page = 1
    response = await RecipeService(db).get_recipe_list(
        current_user=current_user,
        is_favorited=is_favorited,
        is_in_shopping_cart=is_in_shopping_cart,
        tags=tags,
        author=author,
        limit=limit,
        page=page,
        router_prefix=ROUTER_PREFIX,
    )
    logger.info(api_success_log(user=current_user, request=request.url))
    return response


@recipe_router.get("/{id}", status_code=status.HTTP_200_OK, summary="Получение рецепта")
async def get_recipe(
    request: Request, db: DBDep, id: int, current_user: OptionalUserDep
) -> RecipeRead | None:
    response = await RecipeService(db).get_recipe(id=id, current_user=current_user)
    logger.info(api_success_log(user=current_user, request=request.url))
    return response


@recipe_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Создание рецепта",
    description="Доступно только авторизованному пользователю",
)
async def create_recipe(
    request: Request,
    db: DBDep,
    current_user: UserDep,
    recipe_data: RecipeCreateRequest = Body(
        openapi_examples=RecipeCreateRequest.model_config["json_schema_extra"]
    ),
):
    try:
        response = await RecipeService(db).create_recipe(
            current_user=current_user, recipe_data=recipe_data
        )
    except MainDataRecipeAtModifyingException as ex:
        logger.warning(api_exception_log(user=current_user, request=request.url, ex=ex))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ex.detail)
    except TagNotFoundException as ex:
        logger.warning(api_exception_log(user=current_user, request=request.url, ex=ex))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ex.detail)
    except IngredientNotFoundException as ex:
        logger.warning(api_exception_log(user=current_user, request=request.url, ex=ex))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ex.detail)
    logger.info(
        f"Пользователь {current_user.email} успешно создал рецепт {response.id}"
    )
    return response


@recipe_router.patch(
    "/{id}",
    status_code=status.HTTP_200_OK,
    summary="Обновление рецепта",
    description="Доступно только автору данного рецепта",
)
async def update_recipe(
    request: Request,
    db: DBDep,
    current_user: UserDep,
    id: int,
    recipe_data: RecipeUpdateRequest = Body(
        openapi_examples=RecipeUpdateRequest.model_config["json_schema_extra"]
    ),
) -> RecipeRead:
    try:
        response = await RecipeService(db).update_recipe(
            current_user=current_user, id=id, recipe_data=recipe_data
        )
    except OnlyAuthorCanEditRecipeException as ex:
        logger.warning(api_exception_log(user=current_user, request=request.url, ex=ex))
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ex.detail)
    except MainDataRecipeAtModifyingException as ex:
        logger.warning(api_exception_log(user=current_user, request=request.url, ex=ex))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ex.detail)
    except TagNotFoundException as ex:
        logger.warning(api_exception_log(user=current_user, request=request.url, ex=ex))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ex.detail)
    except IngredientNotFoundException as ex:
        logger.warning(api_exception_log(user=current_user, request=request.url, ex=ex))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ex.detail)
    except RecipeNotFoundException as ex:
        logger.warning(api_exception_log(user=current_user, request=request.url, ex=ex))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ex.detail)
    logger.info(f"Пользователь {current_user.email} успешно обновил рецепт {id}")
    return response


@recipe_router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление рецепта",
    description="Доступно только автору данного рецепта",
)
async def delete_recipe(
    request: Request, db: DBDep, current_user: UserDep, id: int
) -> None:
    try:
        response = await RecipeService(db).delete_recipe(
            current_user=current_user, id=id
        )
    except OnlyAuthorCanEditRecipeException as ex:
        logger.warning(api_exception_log(user=current_user, request=request.url, ex=ex))
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ex.detail)
    except RecipeNotFoundException as ex:
        logger.warning(api_exception_log(user=current_user, request=request.url, ex=ex))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ex.detail)
    logger.info(f"Пользователь {current_user.email} успешно удалил рецепт {id}")
    return response


favorite_recipe_router = APIRouter(
    prefix=ROUTER_PREFIX,
    tags=[
        "Избранное",
    ],
)


@favorite_recipe_router.post(
    "/{id}/favorite",
    summary="Добавить рецепт в избранное",
    description="Доступно только авторизованному пользователю",
    status_code=status.HTTP_201_CREATED,
)
async def make_recipe_favorite(
    request: Request,
    id: int,
    db: DBDep,
    current_user: UserDep,
) -> FavoriteRecipeRead:
    try:
        response = await RecipeService(db).make_recipe_favorite(
            id=id, current_user=current_user
        )
    except RecipeAlreadyIsFavoritedException as ex:
        logger.warning(api_exception_log(user=current_user, request=request.url, ex=ex))
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=ex.detail)
    except RecipeNotFoundException as ex:
        logger.warning(api_exception_log(user=current_user, request=request.url, ex=ex))
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=ex.detail)
    logger.info(f"Пользователь {current_user.email} добавил рецепт {id} в избранное")
    return response


@favorite_recipe_router.delete(
    "/{id}/favorite",
    summary="Удалить рецепт из избранного",
    description="Доступно только авторизованным пользователям",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def cancel_favorite_recipe(
    request: Request,
    id: int,
    db: DBDep,
    current_user: UserDep,
) -> None:
    try:
        await RecipeService(db).cancel_favorite_recipe(id=id, current_user=current_user)
        logger.info(
            f"Пользователь {current_user.email} удалил рецепт {id} из избранного"
        )
    except RecipeNotFavoritedException as ex:
        logger.warning(api_exception_log(user=current_user, request=request.url, ex=ex))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ex.detail)


shopping_cart_router = APIRouter(
    prefix=ROUTER_PREFIX,
    tags=[
        "Список покупок",
    ],
)


@shopping_cart_router.get(
    "/download_shopping_cart",
    status_code=status.HTTP_200_OK,
    summary="Скачать список покупок",
    description="Скачать файл со списком покупок.",
)
async def download_shopping_cart(db: DBDep, current_user: UserDep):
    logger.info(f"Пользователь {current_user.email} сгенерировал список покупок")
    return await RecipeService(db).download_shopping_cart(current_user=current_user)


@shopping_cart_router.post(
    "/{id}/shopping_cart",
    summary="Добавить рецепт в список покупок",
    description="Доступно только авторизованным пользователям",
    status_code=status.HTTP_201_CREATED,
)
async def add_recipe_to_shopping_cart(
    request: Request,
    id: int,
    db: DBDep,
    current_user: UserDep,
) -> ShoppingCartRecipeRead:
    try:
        response = await RecipeService(db).add_recipe_to_shopping_cart(
            id=id, current_user=current_user
        )
    except RecipeAlreadyIsInShoppingListException as ex:
        logger.warning(api_exception_log(user=current_user, request=request.url, ex=ex))
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=ex.detail)
    except RecipeNotFoundException as ex:
        logger.warning(api_exception_log(user=current_user, request=request.url, ex=ex))
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=ex.detail)
    logger.info(
        f"Пользователь {current_user.email} добавил рецепт {id} в список покупок"
    )
    return response


@shopping_cart_router.delete(
    "/{id}/shopping_cart",
    summary="Удалить рецепт из списка покупок",
    description="Доступно только авторизованным пользователям",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_recipe_from_shopping_cart(
    request: Request,
    id: int,
    db: DBDep,
    current_user: UserDep,
) -> None:
    try:
        await RecipeService(db).remove_recipe_from_shopping_cart(
            id=id, current_user=current_user
        )
        logger.info(
            f"Пользователь {current_user.email} удалил рецепт {id} из списка покупок"
        )
    except RecipeNotInShoppingListException as ex:
        logger.warning(api_exception_log(user=current_user, request=request.url, ex=ex))
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=ex.detail)
