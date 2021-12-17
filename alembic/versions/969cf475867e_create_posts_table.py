"""create posts table

Revision ID: 969cf475867e
Revises: 
Create Date: 2021-12-16 00:07:06.297013

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "969cf475867e"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "posts",
        sa.Column("id", sa.Integer(), nullable=False, primary_key=True),
        sa.Column("title", sa.String(), nullable=False),
    )


def downgrade():
    op.drop_table("posts")
