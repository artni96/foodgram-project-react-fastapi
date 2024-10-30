from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.src.db import Base


class UserModel(SQLAlchemyBaseUserTable[int], Base):
    username: Mapped[str] = mapped_column(String(32), unique=True)
    first_name: Mapped[str | None] = mapped_column(String(32))
    last_name: Mapped[str | None] = mapped_column(String(32))


class SubscriptionModel(Base):
    author_id: Mapped[int] = mapped_column(
        ForeignKey('user.id', ondelete='CASCADE'))
    subscriber_id: Mapped[int] = mapped_column(
        ForeignKey('user.id', ondelete='CASCADE'))

    __table_args__ = (UniqueConstraint(
        'author_id', 'subscriber_id', name='author cannot be subscriber'
    ),)
