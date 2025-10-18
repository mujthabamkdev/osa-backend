"""add_subjects_table_and_update_chapters

Revision ID: 86d0bfcf33d0
Revises: 0004
Create Date: 2025-10-17 14:56:18.594993

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '86d0bfcf33d0'
down_revision: Union[str, None] = '0004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass