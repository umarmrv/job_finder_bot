"""add published_chat_id to job posts

Revision ID: 20260503_01
Revises: 20260415_01
Create Date: 2026-05-03 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260503_01"
down_revision: Union[str, None] = "20260415_01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {col["name"] for col in inspector.get_columns("job_posts")}
    if "published_chat_id" not in columns:
        op.add_column("job_posts", sa.Column("published_chat_id", sa.BigInteger(), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {col["name"] for col in inspector.get_columns("job_posts")}
    if "published_chat_id" in columns:
        op.drop_column("job_posts", "published_chat_id")
