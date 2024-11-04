"""recipe and recipe tag models created

Revision ID: 07
Revises: 06
Create Date: 2024-11-04 14:39:05.970735

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "07"
down_revision: Union[str, None] = "06"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "recipe",
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("cooking_time", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "cooking_time > 0", name="check_cooking_time_non_negative"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "recipetag",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("recipetag")
    op.drop_table("recipe")
