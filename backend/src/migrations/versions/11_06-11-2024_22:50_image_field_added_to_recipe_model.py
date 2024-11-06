"""image field added to recipe model

Revision ID: 11
Revises: 10
Create Date: 2024-11-06 22:50:13.280151

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "11"
down_revision: Union[str, None] = "10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("recipe", sa.Column("image", sa.String(), nullable=True))
    op.create_unique_constraint(None, "recipe", ["image"])


def downgrade() -> None:
    op.drop_constraint(None, "recipe", type_="unique")
    op.drop_column("recipe", "image")
