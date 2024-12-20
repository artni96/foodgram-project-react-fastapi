from asyncpg import UniqueViolationError, ForeignKeyViolationError
from sqlalchemy.exc import IntegrityError, NoResultFound

from backend.src.exceptions.recipes import OnlyAuthorCanEditRecipeException, RecipeAlreadyIsInShoppingListException, \
    RecipeNotFoundException, RecipeAlreadyIsFavoritedException, RecipeNotInShoppingListException, \
    RecipeNotFavoritedException
from backend.src.schemas.recipes import RecipeListRead, RecipeRead, RecipeCreateRequest, RecipeUpdateRequest, \
    ShoppingCartRecipeRead, ShoppingCartRecipeCreate, FavoriteRecipeRead, FavoriteRecipeCreate
from backend.src.schemas.users import UserReadWithRole
from backend.src.services.base import BaseService


class RecipeService(BaseService):
    async def get_recipe_list(
            self,
            router_prefix: str,
            current_user: UserReadWithRole,
            author: int | None = None,
            tags: list[str] | None = None,
            is_favorited: int = 0,
            is_in_shopping_cart: int = 0,
            page: int | None = None,
            limit: int | None = None,
    ) -> RecipeListRead | None:
        result = await self.db.recipes.get_filtered(
            current_user=current_user,
            is_favorited=is_favorited,
            is_in_shopping_cart=is_in_shopping_cart,
            tags=tags,
            author=author,
            db=self.db,
            limit=limit,
            page=page,
            router_prefix=router_prefix,
        )
        return result

    async def get_recipe(
        self,
        id: int,
        current_user: UserReadWithRole
    ) -> RecipeRead | None:
        result = await self.db.recipes.get_one_or_none(
            id=id,
            current_user=current_user,
            db=self.db
        )
        return result

    async def create_recipe(
            self,
            current_user: UserReadWithRole,
            recipe_data: RecipeCreateRequest
    ):
        recipe = await self.db.recipes.create(
            recipe_data=recipe_data,
            current_user_id=current_user.id,
            db=self.db
        )
        await self.db.commit()
        return recipe

    async def update_recipe(
        self,
        current_user: UserReadWithRole,
        id: int,
        recipe_data: RecipeUpdateRequest,
    ) -> RecipeRead:
        check_recipe = await self.db.recipes.check_recipe_exists(id=id)
        if check_recipe.author != current_user.id:
            raise OnlyAuthorCanEditRecipeException
        recipe = await self.db.recipes.update(
            recipe_data=recipe_data,
            id=id,
            db=self.db
        )
        await self.db.commit()
        return recipe

    async def delete_recipe(
            self,
            current_user: UserReadWithRole,
            id: int
    ) -> None:
        check_recipe = await self.db.recipes.check_recipe_exists(id=id)
        if check_recipe.author == current_user.id:
            recipe = await self.db.recipes.delete(id=id)
            await self.db.commit()
            return recipe
        else:
            raise OnlyAuthorCanEditRecipeException

    async def make_recipe_favorite(
            self,
            id: int,
            current_user: UserReadWithRole,
    ) -> FavoriteRecipeRead:
        favorite_recipe_data = FavoriteRecipeCreate(
            recipe_id=id,
            user_id=current_user.id
        )
        try:
            result = await self.db.favorite_recipes.create(data=favorite_recipe_data)
            await self.db.commit()
            return result
        except IntegrityError as ex:
            if isinstance(ex.orig.__cause__, UniqueViolationError):
                raise RecipeAlreadyIsFavoritedException
            elif isinstance(ex.orig.__cause__, ForeignKeyViolationError):
                raise RecipeNotFoundException

    async def cancel_favorite_recipe(
            self,
            id: int,
            current_user: UserReadWithRole,
    ) -> None:
        try:
            await self.db.favorite_recipes.delete(recipe_id=id, user_id=current_user.id)
            await self.db.commit()
        except NoResultFound:
            raise RecipeNotFavoritedException

    async def download_shopping_cart(
            self,
            current_user: UserReadWithRole
    ):
        get_shopping_cart = await self.db.shopping_cart.get_shopping_cart(
            user_id=current_user.id
        )
        return get_shopping_cart

    async def add_recipe_to_shopping_cart(
        self,
        id: int,
        current_user: UserReadWithRole,
    ) -> ShoppingCartRecipeRead:
        shopping_cart_recipe_data = ShoppingCartRecipeCreate(
            recipe_id=id,
            user_id=current_user.id
        )
        try:
            result = await self.db.shopping_cart.create(data=shopping_cart_recipe_data)
            await self.db.commit()
            return result
        except IntegrityError as ex:
            if isinstance(ex.orig.__cause__, UniqueViolationError):
                raise RecipeAlreadyIsInShoppingListException
            elif isinstance(ex.orig.__cause__, ForeignKeyViolationError):
                raise RecipeNotFoundException

    async def remove_recipe_from_shopping_cart(
        self,
        id: int,
        current_user: UserReadWithRole,
    ) -> None:
        try:
            await self.db.shopping_cart.delete(recipe_id=id, user_id=current_user.id)
            await self.db.commit()
        except NoResultFound:
            raise RecipeNotInShoppingListException
