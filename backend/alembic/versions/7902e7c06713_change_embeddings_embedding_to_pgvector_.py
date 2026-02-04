"""change embeddings.embedding to pgvector and add index

Revision ID: 7902e7c06713
Revises: cc87ed74e223
Create Date: 2026-02-04 17:40:32.395898

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7902e7c06713'
down_revision: Union[str, None] = 'cc87ed74e223'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
