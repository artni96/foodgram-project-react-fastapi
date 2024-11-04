"""measurement_utit field added to ingredient model

Revision ID: 02
Revises: 01
Create Date: 2024-11-03 16:10:55.345322

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "02"
down_revision: Union[str, None] = "01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table("subscription")
    op.add_column(
        "ingredient",
        sa.Column("measurement_unit", sa.String(), nullable=False),
    )


def downgrade() -> None:
    op.drop_column("ingredient", "measurement_unit")
    op.create_table(
        "subscription",
        sa.Column(
            "author_id", sa.INTEGER(), autoincrement=False, nullable=False
        ),
        sa.Column(
            "subscriber_id", sa.INTEGER(), autoincrement=False, nullable=False
        ),
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.CheckConstraint(
            "author_id <> subscriber_id", name="author cannot follow themself"
        ),
        sa.ForeignKeyConstraint(
            ["author_id"],
            ["user.id"],
            name="subscription_author_id_fkey",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["subscriber_id"],
            ["user.id"],
            name="subscription_subscriber_id_fkey",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="subscription_pkey"),
        sa.UniqueConstraint(
            "author_id", "subscriber_id", name="unique subscriptions"
        ),
    )
