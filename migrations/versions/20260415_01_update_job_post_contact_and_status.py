"""update job post contact user and status

Revision ID: 20260415_01
Revises: 20260406_01
Create Date: 2026-04-15 12:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260415_01"
down_revision: Union[str, None] = "20260406_01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {col["name"]: col for col in inspector.get_columns("job_posts")}
    contact_username_col = columns.get("contact_username")
    contact_is_text = contact_username_col is not None and isinstance(contact_username_col["type"], sa.String)

    op.execute("ALTER TYPE job_status_enum ADD VALUE IF NOT EXISTS 'rejected'")

    should_create_contact_user_id = "contact_username" not in columns or contact_is_text
    if should_create_contact_user_id and "contact_user_id" not in columns:
        op.add_column("job_posts", sa.Column("contact_user_id", sa.Integer(), nullable=True))

    inspector = sa.inspect(bind)
    columns = {col["name"]: col for col in inspector.get_columns("job_posts")}
    contact_username_col = columns.get("contact_username")
    contact_is_text = contact_username_col is not None and isinstance(contact_username_col["type"], sa.String)

    if "contact_user_id" in columns and contact_is_text:
        op.execute(
            """
            UPDATE job_posts
            SET contact_user_id = users.id
            FROM users
            WHERE users.username IS NOT NULL
              AND job_posts.contact_username = users.username
            """
        )

        op.execute(
            """
            UPDATE job_posts
            SET contact_user_id = CAST(contact_username AS INTEGER)
            WHERE contact_user_id IS NULL
              AND contact_username ~ '^[0-9]+$'
            """
        )

        op.drop_column("job_posts", "contact_username")
        op.alter_column("job_posts", "contact_user_id", new_column_name="contact_username")

    inspector = sa.inspect(bind)
    columns = {col["name"] for col in inspector.get_columns("job_posts")}
    fks = inspector.get_foreign_keys("job_posts")
    has_contact_fk = any(
        fk.get("referred_table") == "users" and fk.get("constrained_columns") == ["contact_username"]
        for fk in fks
    )

    if "contact_username" in columns and not has_contact_fk:
        op.create_foreign_key(
            "fk_job_posts_contact_username_users",
            "job_posts",
            "users",
            ["contact_username"],
            ["id"],
        )

    # Safety cleanup for previously inconsistent upgrades where contact_user_id
    # was created on an already migrated schema.
    if "contact_username" in columns and "contact_user_id" in columns and not contact_is_text:
        op.drop_column("job_posts", "contact_user_id")


def downgrade() -> None:
    op.drop_constraint("fk_job_posts_contact_username_users", "job_posts", type_="foreignkey")
    op.alter_column("job_posts", "contact_username", new_column_name="contact_user_id")
    op.add_column("job_posts", sa.Column("contact_username", sa.String(length=100), nullable=True))

    op.execute(
        """
        UPDATE job_posts
        SET contact_username = contact_user_id::text
        WHERE contact_user_id IS NOT NULL
        """
    )

    op.drop_column("job_posts", "contact_user_id")
