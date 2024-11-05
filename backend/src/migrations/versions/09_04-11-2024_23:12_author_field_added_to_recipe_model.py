"""author field added to recipe model

Revision ID: 09
Revises: 08
Create Date: 2024-11-04 23:12:50.499962

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "09"
down_revision: Union[str, None] = "08"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("recipe", sa.Column("author", sa.Integer(), nullable=False))
    op.create_foreign_key(
        None, "recipe", "user", ["author"], ["id"], ondelete="cascade"
    )
    op.drop_constraint(
        "recipetag_recipe_id_fkey", "recipetag", type_="foreignkey"
    )
    op.drop_constraint(
        "recipetag_tag_id_fkey", "recipetag", type_="foreignkey"
    )
    op.create_foreign_key(
        None,
        "recipetag",
        "tag",
        ["tag_id"],
        ["id"],
        onupdate="cascade",
        ondelete="cascade",
    )
    op.create_foreign_key(
        None,
        "recipetag",
        "recipe",
        ["recipe_id"],
        ["id"],
        onupdate="cascade",
        ondelete="cascade",
    )


def downgrade() -> None:
    op.drop_constraint(None, "recipetag", type_="foreignkey")
    op.drop_constraint(None, "recipetag", type_="foreignkey")
    op.create_foreign_key(
        "recipetag_tag_id_fkey", "recipetag", "tag", ["tag_id"], ["id"]
    )
    op.create_foreign_key(
        "recipetag_recipe_id_fkey",
        "recipetag",
        "recipe",
        ["recipe_id"],
        ["id"],
    )
    op.drop_constraint(None, "recipe", type_="foreignkey")
    op.drop_column("recipe", "author")
