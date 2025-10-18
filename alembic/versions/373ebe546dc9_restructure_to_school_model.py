"""restructure_to_school_model

Revision ID: 373ebe546dc9
Revises: 9e5b38dceec7
Create Date: 2025-10-17 15:40:59.299300

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '373ebe546dc9'
down_revision: Union[str, None] = '9e5b38dceec7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass