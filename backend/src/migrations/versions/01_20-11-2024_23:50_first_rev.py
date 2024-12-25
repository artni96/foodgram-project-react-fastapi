"""first rev

Revision ID: 01
Revises:
Create Date: 2024-11-20 23:50:25.823391

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
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "image",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("base64", sa.String(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "ingredient",
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("measurement_unit", sa.String(length=200), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", "measurement_unit", name="unique ingredients"),
    )
    op.create_table(
        "tag",
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("color", sa.String(length=7), nullable=True),
        sa.Column("slug", sa.String(length=200), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_table(
        "user",
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("username", sa.String(length=150), nullable=False),
        sa.Column("first_name", sa.String(length=150), nullable=True),
        sa.Column("last_name", sa.String(length=150), nullable=True),
        sa.Column("hashed_password", sa.String(length=150), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_superuser", sa.Boolean(), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("username"),
    )
    op.create_table(
        "ingredientamount",
        sa.Column("ingredient_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["ingredient_id"],
            ["ingredient.id"],
            onupdate="cascade",
            ondelete="cascade",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "recipe",
        sa.Column("author", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("cooking_time", sa.Integer(), nullable=False),
        sa.Column("image", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.CheckConstraint("cooking_time > 0", name="check_cooking_time_non_negative"),
        sa.ForeignKeyConstraint(["author"], ["user.id"], ondelete="cascade"),
        sa.ForeignKeyConstraint(
            ["image"],
            ["image.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "subscription",
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column("subscriber_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "author_id <> subscriber_id", name="author cannot follow themself"
        ),
        sa.ForeignKeyConstraint(["author_id"], ["user.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["subscriber_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("author_id", "subscriber_id", name="unique subscriptions"),
    )
    op.create_table(
        "favoriterecipe",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("recipe_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["recipe_id"], ["recipe.id"], ondelete="cascade"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="cascade"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "recipe_id", name="unique favorite recipe"),
    )
    op.create_table(
        "recipeingredient",
        sa.Column("ingredient_amount_id", sa.Integer(), nullable=False),
        sa.Column("recipe_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["ingredient_amount_id"],
            ["ingredientamount.id"],
            onupdate="cascade",
            ondelete="cascade",
        ),
        sa.ForeignKeyConstraint(
            ["recipe_id"],
            ["recipe.id"],
            onupdate="cascade",
            ondelete="cascade",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "recipetag",
        sa.Column("tag_id", sa.Integer(), nullable=False),
        sa.Column("recipe_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["recipe_id"],
            ["recipe.id"],
            onupdate="cascade",
            ondelete="cascade",
        ),
        sa.ForeignKeyConstraint(
            ["tag_id"], ["tag.id"], onupdate="cascade", ondelete="cascade"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "shoppingcart",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("recipe_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["recipe_id"], ["recipe.id"], ondelete="cascade"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="cascade"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id", "recipe_id", name="unique recipe in shopping cart"
        ),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("shoppingcart")
    op.drop_table("recipetag")
    op.drop_table("recipeingredient")
    op.drop_table("favoriterecipe")
    op.drop_table("subscription")
    op.drop_table("recipe")
    op.drop_table("ingredientamount")
    op.drop_table("user")
    op.drop_table("tag")
    op.drop_table("ingredient")
    op.drop_table("image")
    # ### end Alembic commands ###
