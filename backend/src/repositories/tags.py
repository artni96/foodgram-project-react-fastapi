from backend.src.repositories.base import BaseRepository
from backend.src.models.tags import TagModel, RecipeTagModel
from backend.src.schemas.tags import TagRead
from pydantic import BaseModel
from sqlalchemy import insert


class TagRepository(BaseRepository):
    model = TagModel
    schema = TagRead


class RecipeTagRepository(BaseRepository):
    model = RecipeTagModel
