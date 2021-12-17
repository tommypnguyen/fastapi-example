"""Add foreign key to posts table

Revision ID: f474fe4fcec6
Revises: cd9967fb060e
Create Date: 2021-12-16 00:37:48.408628

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f474fe4fcec6"
down_revision = "cd9967fb060e"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("posts", sa.Column("user_id", sa.Integer(), nullable=False))
    op.create_foreign_key(
        "posts_users_fk",
        source_table="posts",
        referent_table="users",
        local_cols=["user_id"],
        remote_cols=["id"],
        ondelete="CASCADE",
    )


def downgrade():
    op.drop_constraint("posts_users_fk", table_name="posts")
    op.drop_column("posts", "user_id")
