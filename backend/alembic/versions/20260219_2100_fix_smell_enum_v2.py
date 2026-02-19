"""Fix missing_docstring in smelltype enum v2

Revision ID: fix_smell_enum_v2
Revises: 20260219_add_smell_enum
Create Date: 2026-02-19 21:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'fix_smell_enum_v2'
down_revision: Union[str, None] = '20260219_add_smell_enum'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Ensure we run outside of a transaction for ALTER TYPE
    with op.get_context().autocommit_block():
        # Attempt to add the value. 
        # using IF NOT EXISTS to prevent errors if it somehow partially succeeded before
        op.execute("ALTER TYPE smelltype ADD VALUE IF NOT EXISTS 'missing_docstring'")

def downgrade() -> None:
    pass
