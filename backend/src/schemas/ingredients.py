from pydantic import BaseModel, ConfigDict, Field

from backend.src.constants import PARAMS_MAX_LENGTH


class IngredientCreate(BaseModel):
    name: str = Field(max_length=PARAMS_MAX_LENGTH)
    measurement_unit: str = Field(max_length=PARAMS_MAX_LENGTH)

    model_config = ConfigDict(from_attributes=True)


class IngredientRead(IngredientCreate):
    id: int


class IngredientAmountCreateRequest(BaseModel):
    id: int
    amount: int


class IngredientAmountCreate(BaseModel):
    ingredient_id: int
    amount: int


class IngredientAmountRead(IngredientAmountCreate):
    id: int


class RecipeIngredientAmountCreate(BaseModel):
    recipe_id: int
    ingredient_amount_id: int


class RecipeIngredientAmountRead(BaseModel):
    id: int
    name: str
    measurement_unit: str
    amount: int
