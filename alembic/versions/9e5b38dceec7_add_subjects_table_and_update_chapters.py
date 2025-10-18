"""add_subjects_table_and_update_chapters

Revision ID: 9e5b38dceec7
Revises: 86d0bfcf33d0
Create Date: 2025-10-17 14:57:11.846493

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9e5b38dceec7'
down_revision: Union[str, None] = '86d0bfcf33d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if subjects table exists, if not create it
    conn = op.get_bind()
    result = conn.execute(sa.text("SELECT name FROM sqlite_master WHERE type='table' AND name='subjects';"))
    if not result.fetchone():
        # Create subjects table
        op.create_table(
            "subjects",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("course_id", sa.Integer(), sa.ForeignKey("courses.id"), nullable=False),
            sa.Column("title", sa.String(255), nullable=False),
            sa.Column("description", sa.Text(), nullable=False, server_default=""),
            sa.Column("order", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )

    # Use batch mode for SQLite to modify chapters table
    with op.batch_alter_table("chapters") as batch_op:
        # Check if subject_id column exists
        result = conn.execute(sa.text("PRAGMA table_info(chapters);"))
        columns = [row[1] for row in result]
        if "subject_id" not in columns:
            batch_op.add_column(sa.Column("subject_id", sa.Integer(), nullable=True))
        batch_op.alter_column("course_id", nullable=True)

    # Use batch mode for SQLite to modify attachments table
    with op.batch_alter_table("attachments") as batch_op:
        # Check if subject_id column exists
        result = conn.execute(sa.text("PRAGMA table_info(attachments);"))
        columns = [row[1] for row in result]
        if "subject_id" not in columns:
            batch_op.add_column(sa.Column("subject_id", sa.Integer(), nullable=True))


def downgrade() -> None:
    # Use batch mode for SQLite to remove columns
    with op.batch_alter_table("attachments") as batch_op:
        batch_op.drop_column("subject_id")

    with op.batch_alter_table("chapters") as batch_op:
        batch_op.drop_column("subject_id")
        batch_op.alter_column("course_id", nullable=False)

    # Drop subjects table
    op.drop_table("subjects")