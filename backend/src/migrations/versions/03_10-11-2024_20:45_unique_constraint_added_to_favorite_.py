"""unique constraint added to favorite recipe model

Revision ID: 03
Revises: 02
Create Date: 2024-11-10 20:45:36.024317

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "03"
down_revision: Union[str, None] = "02"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        "unique favorite recipe", "favoriterecipe", ["user_id", "recipe_id"]
    )


def downgrade() -> None:
    op.drop_constraint(
        "unique favorite recipe", "favoriterecipe", type_="unique"
    )
