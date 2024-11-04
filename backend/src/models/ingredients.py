from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, UniqueConstraint

from backend.src.base import Base


class IngredientModel(Base):
    name: Mapped[str] = mapped_column(String(200))
    measurement_unit: Mapped[str] = mapped_column(String(200))

    __table_args__ = (
        UniqueConstraint(
            'name', 'measurement_unit', name='unique ingredients'
        ),
    )
