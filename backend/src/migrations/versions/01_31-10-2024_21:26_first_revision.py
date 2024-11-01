"""first revision

Revision ID: 01
Revises: 
Create Date: 2024-10-31 21:26:20.933217

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "01"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        "author cannot be subscriber", "subscription", type_="unique"
    )


def downgrade() -> None:
    op.create_unique_constraint(
        "author cannot be subscriber",
        "subscription",
        ["author_id", "subscriber_id"],
    )
