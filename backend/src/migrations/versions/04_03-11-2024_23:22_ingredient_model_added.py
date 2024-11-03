"""ingredient model added

Revision ID: 04
Revises: 03
Create Date: 2024-11-03 23:22:44.000602

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "04"
down_revision: Union[str, None] = "03"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ingredient",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("measurement_unit", sa.String(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("ingredient")
