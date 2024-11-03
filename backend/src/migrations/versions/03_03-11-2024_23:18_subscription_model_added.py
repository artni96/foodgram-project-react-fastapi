"""subscription model added

Revision ID: 03
Revises: 02
Create Date: 2024-11-03 23:18:23.610348

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "03"
down_revision: Union[str, None] = "02"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "subscription",
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column("subscriber_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "author_id <> subscriber_id", name="author cannot follow themself"
        ),
        sa.ForeignKeyConstraint(
            ["author_id"], ["user.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["subscriber_id"], ["user.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "author_id", "subscriber_id", name="unique subscriptions"
        ),
    )


def downgrade() -> None:
    op.drop_table("subscription")
