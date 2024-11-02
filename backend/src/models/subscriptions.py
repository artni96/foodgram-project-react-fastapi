from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.src.db import Base


class SubscriptionModel(Base):
    author_id: Mapped[int] = mapped_column(
        ForeignKey('user.id', ondelete='CASCADE'))
    subscriber_id: Mapped[int] = mapped_column(
        ForeignKey('user.id', ondelete='CASCADE'))

    __table_args__ = (
        CheckConstraint(
            sqltext="author_id <> subscriber_id",
            name='author cannot follow themself'
        ),
        UniqueConstraint(
            'author_id', 'subscriber_id', name='unique subscriptions'
        ),
    )
