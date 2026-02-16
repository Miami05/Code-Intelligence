"""create call_relationships table

Revision ID: 005
Revises: 004
Create Date: 2026-02-17 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create call_relationships table
    op.create_table(
        "call_relationships",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "repository_id",
            UUID(as_uuid=True),
            sa.ForeignKey("repositories.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "caller_symbol_id",
            UUID(as_uuid=True),
            sa.ForeignKey("symbols.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("caller_name", sa.String(), nullable=False),
        sa.Column("caller_file", sa.String(), nullable=False),
        sa.Column("callee_name", sa.String(), nullable=False),
        sa.Column("callee_file", sa.String(), nullable=True),
        sa.Column(
            "callee_symbol_id",
            UUID(as_uuid=True),
            sa.ForeignKey("symbols.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("call_line", sa.Integer(), nullable=False),
        sa.Column("is_external", sa.Boolean(), default=False, nullable=False),
    )

    # Create indexes
    op.create_index("idx_caller_symbol_id", "call_relationships", ["caller_symbol_id"])
    op.create_index("idx_callee_symbol_id", "call_relationships", ["callee_symbol_id"])
    op.create_index("idx_repository_calls", "call_relationships", ["repository_id"])


def downgrade() -> None:
    # Drop indexes
    op.drop_index("idx_repository_calls", "call_relationships")
    op.drop_index("idx_callee_symbol_id", "call_relationships")
    op.drop_index("idx_caller_symbol_id", "call_relationships")

    # Drop table
    op.drop_table("call_relationships")
