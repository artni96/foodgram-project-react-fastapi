from pydantic import BaseModel, ConfigDict, Field

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
                        ]
                    }
                }
            }
        }


class RecipeCreate(BaseRecipe):
    author: int


class RecipeAfterCreateRead(RecipeCreate):
    id: int
    author: FollowedUserRead


class RecipeRead(RecipeAfterCreateRead):
    tag: list[TagRead] = []
    ingredient: list[RecipeIngredientAmountRead] = []
    is_favorited: bool = True
    is_in_shopping_cart: bool = True
