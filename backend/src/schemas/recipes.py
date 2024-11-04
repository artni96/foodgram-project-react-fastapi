from pydantic import BaseModel, Field, ConfigDict
from backend.src.constants import PARAMS_MAX_LENGTH
from backend.src.schemas.tags import TagRead


class RecipeCreateRequest(BaseModel):
    name: str = Field(max_length=PARAMS_MAX_LENGTH)
    text: str
    cooking_time: int = Field()
    tag: list[int] = []

    model_config = ConfigDict(from_attributes=True)


class RecipeCreate(BaseModel):
    name: str = Field(max_length=PARAMS_MAX_LENGTH)
    text: str
    cooking_time: int = Field()

    model_config = ConfigDict(from_attributes=True)


class RecipeRead(RecipeCreate):
    id: int
    tag: list[TagRead]
