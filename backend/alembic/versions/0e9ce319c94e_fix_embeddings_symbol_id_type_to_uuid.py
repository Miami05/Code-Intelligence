"""fix embeddings symbol_id type to uuid

Revision ID: 0e9ce319c94e
Revises: 7902e7c06713
Create Date: 2026-02-04 19:00:59.258010

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0e9ce319c94e"
down_revision: Union[str, None] = "7902e7c06713"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Change symbol_id and id from String to UUID
    op.execute("ALTER TABLE embeddings ALTER COLUMN id TYPE UUID USING id::uuid")
    op.execute(
        "ALTER TABLE embeddings ALTER COLUMN symbol_id TYPE UUID USING symbol_id::uuid"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE embeddings ALTER COLUMN symbol_id TYPE VARCHAR USING symbol_id::text"
    )
    op.execute("ALTER TABLE embeddings ALTER COLUMN id TYPE VARCHAR USING id::text")
