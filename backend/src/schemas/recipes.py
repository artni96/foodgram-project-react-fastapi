from pydantic import BaseModel, Field, ConfigDict
from backend.src.constants import PARAMS_MAX_LENGTH
from backend.src.schemas.tags import TagRead
from backend.src.schemas.users import FollowedUserRead
from backend.src.schemas.ingredients import IngredientAmountCreateRequest


class BaseRecipe(BaseModel):
    name: str = Field(max_length=PARAMS_MAX_LENGTH)
    text: str
    cooking_time: int = Field()

    model_config = ConfigDict(from_attributes=True)


class RecipeCreateRequest(BaseRecipe):

    tag: list[int] = []
    ingredient: list[IngredientAmountCreateRequest] = []


class RecipeCreate(BaseRecipe):
    author: int


class RecipeRead(RecipeCreate):
    id: int
    author: int


class RecipeWithTagsRead(BaseRecipe):
    # tag: list[TagRead] = []
    # ingredient: list[IngredientAmountCreateRequest] = []
    id: int
    author: FollowedUserRead
