"""Add parent-student link table for admin approvals

Revision ID: 20251025_admin_parent_student_links
Revises: 20251019_teacher_feature_tables
Create Date: 2025-10-25 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20251025_admin_parent_student_links"
down_revision: Union[str, None] = "20251019_teacher_feature_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "parent_students",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("parent_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("student_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("parent_id", "student_id", name="uq_parent_student"),
    )
    op.create_index("ix_parent_students_parent_id", "parent_students", ["parent_id"])
    op.create_index("ix_parent_students_student_id", "parent_students", ["student_id"])


def downgrade() -> None:
    op.drop_index("ix_parent_students_student_id", table_name="parent_students")
    op.drop_index("ix_parent_students_parent_id", table_name="parent_students")
    op.drop_table("parent_students")
