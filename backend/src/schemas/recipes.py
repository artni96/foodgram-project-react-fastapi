from pydantic import BaseModel, ConfigDict, Field

from backend.src.constants import PARAMS_MAX_LENGTH
from backend.src.schemas.ingredients import (
    IngredientAmountCreateRequest,
    RecipeIngredientAmountRead,
)
from backend.src.schemas.tags import TagRead
from backend.src.schemas.users import FollowedUserRead


class BaseRecipe(BaseModel):
    name: str = Field(max_length=PARAMS_MAX_LENGTH)
    text: str
    cooking_time: int

    model_config = ConfigDict(from_attributes=True)


class RecipeCreateUpdateBaseRequest(BaseRecipe):
    tags: list[int] = []
    ingredients: list[IngredientAmountCreateRequest] = []

    model_config = {
        "json_schema_extra": {
            "Тестовый рецепт": {
                "summary": "Тестовый рецепт",
                "value": {
                    "name": "string",
                    "text": "string",
                    "cooking_time": 1,
                    "tags": [1, 2],
                    "ingredients": [
                        {"id": 1, "amount": 100},
                        {"id": 2, "amount": 200},
                    ],
                    "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",  # noqa
                },
            }
        }
    }


class RecipeCreateRequest(RecipeCreateUpdateBaseRequest):
    image: str


class RecipeCreate(BaseRecipe):
    author: int
    image: str


class RecipeUpdateRequest(RecipeCreateUpdateBaseRequest):
    image: str | None = None


class RecipeUpdate(BaseRecipe):
    id: int
    image: str | None


class RecipeAfterCreateRead(RecipeCreate):
    id: int
    author: FollowedUserRead
    image: str


class RecipeRead(RecipeAfterCreateRead):
    tags: list[TagRead] = []
    ingredients: list[RecipeIngredientAmountRead] = []
    is_favorited: bool = False
    is_in_shopping_cart: bool = False


class CheckRecipeRead(BaseModel):
    author: int
    id: int


class ImageRead(BaseModel):
    id: int
    name: str
    base64: str


class FavoriteRecipeCreate(BaseModel):
    recipe_id: int
    user_id: int


class FavoriteRecipeRead(BaseModel):
    id: int
    name: str
    image: str
    cooking_time: int


class ShoppingCartRecipeCreate(FavoriteRecipeCreate):
    pass


class ShoppingCartRecipeRead(FavoriteRecipeRead):
    pass


class RecipeListRead(BaseModel):
    count: int
    next: str | None = None
    previous: str | None = None
    results: list[RecipeRead] = []
