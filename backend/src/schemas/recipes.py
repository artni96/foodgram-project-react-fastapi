from pydantic import BaseModel, ConfigDict, Field, AnyHttpUrl

from backend.src.constants import PARAMS_MAX_LENGTH
from backend.src.schemas.ingredients import (IngredientAmountCreateRequest,
                                             RecipeIngredientAmountRead)
from backend.src.schemas.tags import TagRead
from backend.src.schemas.users import FollowedUserRead


class BaseRecipe(BaseModel):
    name: str = Field(max_length=PARAMS_MAX_LENGTH)
    text: str
    cooking_time: int = Field()

    model_config = ConfigDict(from_attributes=True)


class RecipeCreateRequest(BaseRecipe):

    tag: list[int] = []
    ingredient: list[IngredientAmountCreateRequest] = []
    image: str

    class Config:
        schema_extra = {
            'examples': {
                'Тестовый рецепт': {
                    'summary': 'Тестовый рецепт',
                    'value': {
                        "name": "string",
                        "text": "string",
                        "cooking_time": 1,
                        "tag": [4, 5],
                        "ingredient": [
                            {'id': 1, 'amount': 100},
                            {'id': 2, 'amount': 200},
                        ],
                        "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==" # noqa
                    }
                }
            }
        }


class RecipeCreate(BaseRecipe):
    author: int
    image: str


class RecipeUpdateRequest(RecipeCreateRequest):
    pass


class RecipeUpdate(BaseRecipe):
    id: int
    image: str


class RecipeAfterCreateRead(RecipeCreate):
    id: int
    author: FollowedUserRead
    image: AnyHttpUrl


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
    image: AnyHttpUrl
    cooking_time: int


class ShoppingCartRecipeCreate(FavoriteRecipeCreate):
    pass


class ShoppingCartRecipeRead(FavoriteRecipeRead):
    pass
