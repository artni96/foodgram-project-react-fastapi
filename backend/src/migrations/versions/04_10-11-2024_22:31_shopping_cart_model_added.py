"""shopping cart model added

Revision ID: 04
Revises: 03
Create Date: 2024-11-10 22:31:31.194014

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "04"
down_revision: Union[str, None] = "03"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "shoppingcart",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("recipe_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["recipe_id"], ["recipe.id"], ondelete="cascade"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="cascade"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id", "recipe_id", name="unique recipe in shopping cart"
        ),
    )


def downgrade() -> None:
    op.drop_table("shoppingcart")
