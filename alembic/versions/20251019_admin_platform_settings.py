"""Add platform settings table for admin configuration

Revision ID: 20251019_admin_platform_settings
Revises: 20251019_teacher_feature_tables
Create Date: 2025-10-19 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20251019_admin_platform_settings"
down_revision: Union[str, None] = "20251019_teacher_feature_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "platform_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("key", sa.String(length=100), nullable=False, unique=True),
        sa.Column("value", sa.JSON(), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            server_onupdate=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_platform_settings_key", "platform_settings", ["key"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_platform_settings_key", table_name="platform_settings")
    op.drop_table("platform_settings")
