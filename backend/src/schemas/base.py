from pydantic import BaseModel


class ShortRecipeRead(BaseModel):
    id: int
    name: str
    image: str
    cooking_time: int
