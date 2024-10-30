from backend.src.repositories.base import BaseRepository
from backend.src.models.users import UserModel
from backend.src.schemas.users import BaseUserRead


class UserRepository(BaseRepository):
    model = UserModel
    schema = BaseUserRead
