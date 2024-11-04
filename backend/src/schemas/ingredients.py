from pydantic import BaseModel, ConfigDict, Field

from backend.src.constants import PARAMS_MAX_LENGTH


class IngredientCreate(BaseModel):
    name: str = Field(max_length=PARAMS_MAX_LENGTH)
    measurement_unit: str = Field(max_length=PARAMS_MAX_LENGTH)

    model_config = ConfigDict(from_attributes=True)


class IngredientRead(IngredientCreate):
    id: int
