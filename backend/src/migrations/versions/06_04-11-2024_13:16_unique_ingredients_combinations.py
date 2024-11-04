"""unique ingredients combinations

Revision ID: 06
Revises: 05
Create Date: 2024-11-04 13:16:20.687798

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "06"
down_revision: Union[str, None] = "05"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        "unique ingredients", "ingredient", ["name", "measurement_unit"]
    )


def downgrade() -> None:
    op.drop_constraint("unique ingredients", "ingredient", type_="unique")
