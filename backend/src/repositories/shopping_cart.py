from backend.src.repositories.favorite_recipes import FavoriteRecipeRepository
from backend.src.models.recipes import ShoppingCartModel
from backend.src.schemas.recipes import ShoppingCartRecipeRead


class ShoppingCartRepository(FavoriteRecipeRepository):
    model = ShoppingCartModel
    schema = ShoppingCartRecipeRead
