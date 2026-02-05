"""initial state

Revision ID: 3ee429a0c576
Revises:
Create Date: 2025-12-24 19:31:01.056508

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3ee429a0c576"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "embeddings",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("symbol_id", sa.String(), nullable=False, unique=True, index=True),
        sa.Column("embedding", sa.ARRAY(sa.Float()), nullable=False),
        sa.Column("model", sa.String(length=100), nullable=False),
        sa.Column("dimensions", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    pass
