from sqlalchemy.orm import Mapped

from backend.src.base import Base


class IngredientModel(Base):
    name: Mapped[str]
