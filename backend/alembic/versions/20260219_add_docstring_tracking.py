"""Add docstring tracking to symbols

Revision ID: 20260219_add_docstring_tracking
Revises: 874d67e7b43c
Create Date: 2026-02-19 13:08:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260219_add_docstring_tracking'
down_revision: Union[str, None] = '874d67e7b43c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add docstring tracking columns to symbols table
    op.add_column('symbols', sa.Column('docstring', sa.Text(), nullable=True))
    op.add_column('symbols', sa.Column('has_docstring', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('symbols', sa.Column('docstring_length', sa.Integer(), nullable=True))
    
    # Add index for fast filtering of undocumented symbols
    op.create_index('ix_symbols_has_docstring', 'symbols', ['has_docstring'])


def downgrade() -> None:
    # Remove docstring tracking
    op.drop_index('ix_symbols_has_docstring', table_name='symbols')
    op.drop_column('symbols', 'docstring_length')
    op.drop_column('symbols', 'has_docstring')
    op.drop_column('symbols', 'docstring')
