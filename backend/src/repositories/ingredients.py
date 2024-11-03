from backend.src.base import IngredientModel
from backend.src.repositories.base import BaseRepository
from backend.src.schemas.ingredients import IngredientRead


class IngredientRepository(BaseRepository):
    model = IngredientModel
    schema = IngredientRead
