"""subscription model field names changed

Revision ID: 03
Revises: 02
Create Date: 2024-10-30 23:13:17.141987

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
        sa.ForeignKeyConstraint(
            ["author_id"], ["user.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["subscriber_id"], ["user.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.drop_table("usersubscription")


def downgrade() -> None:
    op.create_table(
        "usersubscription",
        sa.Column("autor", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column(
            "subscriber", sa.INTEGER(), autoincrement=False, nullable=False
        ),
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.ForeignKeyConstraint(
            ["autor"],
            ["user.id"],
            name="usersubscription_autor_fkey",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["subscriber"],
            ["user.id"],
            name="usersubscription_subscriber_fkey",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="usersubscription_pkey"),
    )
    op.drop_table("subscription")
