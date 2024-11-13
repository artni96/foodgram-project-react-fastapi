from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.src.constants import USER_PARAMS_MAX_LENGTH
from backend.src.db import Base


class UserModel(SQLAlchemyBaseUserTable[int], Base):
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
    recipe: Mapped[list['RecipeModel']] = relationship(
        back_populates='author_info'
    )
