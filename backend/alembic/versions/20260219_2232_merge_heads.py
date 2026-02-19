"""merge heads

Revision ID: merge_heads_final
Revises: f51a6709cc45, create_code_smells
Create Date: 2026-02-19 22:32:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'merge_heads_final'
down_revision: Union[str, None] = ('f51a6709cc45', 'create_code_smells')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Merge migration - no changes needed
    pass


def downgrade() -> None:
    # Merge migration - no changes needed
    pass
