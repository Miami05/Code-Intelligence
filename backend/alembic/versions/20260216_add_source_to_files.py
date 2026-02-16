"""add source to files table

Revision ID: 004
Revises: 003
Create Date: 2026-02-16 20:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add source column to files table to store file content for call graph analysis
    op.add_column('files',
        sa.Column('source', sa.Text(), nullable=True)
    )


def downgrade() -> None:
    # Drop source column
    op.drop_column('files', 'source')
