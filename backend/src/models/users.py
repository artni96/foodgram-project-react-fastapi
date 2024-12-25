import typing

from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.src.constants import USER_PARAMS_MAX_LENGTH, MAX_EMAIL_LENGTH
from backend.src.db import Base

if typing.TYPE_CHECKING:
    from backend.src.models.recipes import RecipeModel

class UserModel(Base):
    email: Mapped[str] = mapped_column(
        String(MAX_EMAIL_LENGTH),
        unique=True
    )
    username: Mapped[str] = mapped_column(
        String(USER_PARAMS_MAX_LENGTH),
        unique=True
    )
    first_name: Mapped[str | None] = mapped_column(
        String(USER_PARAMS_MAX_LENGTH)
    )
    last_name: Mapped[str | None] = mapped_column(
        String(USER_PARAMS_MAX_LENGTH)
    )
    hashed_password: Mapped[str] = mapped_column(
        String(USER_PARAMS_MAX_LENGTH)
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=True)
    recipe: Mapped[list['RecipeModel']] = relationship(
        back_populates='author_info'
    )
