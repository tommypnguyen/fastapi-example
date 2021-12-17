"""Add content column to posts table

Revision ID: 2a9dd26a8240
Revises: 969cf475867e
Create Date: 2021-12-16 00:20:09.930366

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2a9dd26a8240"
down_revision = "969cf475867e"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("posts", sa.Column("content", sa.String(), nullable=False))


def downgrade():
    op.drop_column("posts", "content")
