"""add approval and ownership to job posts

Revision ID: 20260406_01
Revises:
Create Date: 2026-04-06 16:40:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260406_01"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE job_status_enum ADD VALUE IF NOT EXISTS 'approved'")

    op.add_column(
        "job_posts",
        sa.Column("user_id", sa.Integer(), nullable=True),
    )
    op.add_column(
        "job_posts",
        sa.Column("published_message_id", sa.Integer(), nullable=True),
    )
    op.create_index(op.f("ix_job_posts_user_id"), "job_posts", ["user_id"], unique=False)

    op.execute("UPDATE job_posts SET user_id = 1 WHERE user_id IS NULL")
    op.alter_column("job_posts", "user_id", existing_type=sa.Integer(), nullable=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_job_posts_user_id"), table_name="job_posts")
    op.drop_column("job_posts", "published_message_id")
    op.drop_column("job_posts", "user_id")

