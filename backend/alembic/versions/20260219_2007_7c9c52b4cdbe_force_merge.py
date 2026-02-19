"""force merge

Revision ID: 7c9c52b4cdbe
Revises: f51a6709cc45, fix_smell_enum_v2
Create Date: 2026-02-19 20:07:39.626942+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7c9c52b4cdbe'
down_revision: Union[str, None] = ('f51a6709cc45', 'fix_smell_enum_v2')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
