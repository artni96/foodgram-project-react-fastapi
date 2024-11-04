from backend.src.repositories.base import BaseRepository
from backend.src.models.tags import TagModel, RecipeTagModel
from backend.src.schemas.tags import TagRead


class TagRepository(BaseRepository):
    model = TagModel
    schema = TagRead


class RecipeTagRepository(BaseRepository):
    model = RecipeTagModel