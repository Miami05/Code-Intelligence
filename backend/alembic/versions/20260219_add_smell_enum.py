"""Add missing_docstring to SmellType enum

Revision ID: 20260219_add_smell_enum
Revises: 20260219_add_docstring_tracking
Create Date: 2026-02-19 13:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260219_add_smell_enum'
down_revision: Union[str, None] = '20260219_add_docstring_tracking'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # PostgreSQL ENUMs are distinct types and need explicit alteration
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE smelltype ADD VALUE IF NOT EXISTS 'missing_docstring'")


def downgrade() -> None:
    # Downgrading enums in Postgres is complex (requires type recreation)
    # For now, we leave the enum value as it doesn't break older schemas
    pass
