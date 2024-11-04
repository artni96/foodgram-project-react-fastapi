from backend.src.repositories.base import BaseRepository
from backend.src.models.tags import TagModel
from backend.src.schemas.tags import TagRead


class TagRepository(BaseRepository):
    model = TagModel
    schema = TagRead
