"""Fix missing_docstring in smelltype enum v3

Revision ID: fix_smell_enum_v3
Revises: 7c9c52b4cdbe
Create Date: 2026-02-19 21:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'fix_smell_enum_v3'
down_revision: Union[str, None] = '7c9c52b4cdbe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Explicitly add the value, letting it fail if something is wrong so we see the error.
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE smelltype ADD VALUE IF NOT EXISTS 'missing_docstring'")

def downgrade() -> None:
    pass
