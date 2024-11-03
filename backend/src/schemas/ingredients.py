from pydantic import BaseModel, ConfigDict


class IngredientRead(BaseModel):
    id: int
    name: str
    measurement_unit: str

    model_config = ConfigDict(from_attributes=True)
