"""favorite recipe model added

Revision ID: 02
Revises: 01
Create Date: 2024-11-10 20:18:48.602864

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "02"
down_revision: Union[str, None] = "01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "favoriterecipe",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("recipe_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["recipe_id"], ["recipe.id"], ondelete="cascade"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="cascade"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("favoriterecipe")
