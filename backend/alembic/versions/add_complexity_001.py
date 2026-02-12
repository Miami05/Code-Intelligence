"""add complexity metrics

Revision ID: add_complexity_001
Revises:
Create Date: 2026-02-09
"""

import sqlalchemy as sa
from alembic import op

revision = "add_complexity_001"
down_revision = "5986bcc38984"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "symbols", sa.Column("cyclomatic_complexity", sa.Integer(), nullable=True)
    )
    op.add_column(
        "symbols", sa.Column("maintainability_index", sa.Float(), nullable=True)
    )
    op.add_column("symbols", sa.Column("lines_of_code", sa.Integer(), nullable=True))
    op.add_column("symbols", sa.Column("comment_lines", sa.Integer(), nullable=True))
    op.create_index("idx_symbols_complexity", "symbols", ["cyclomatic_complexity"])


def downgrade():
    op.drop_index("idx_symbols_complexity")
    op.drop_column("symbols", "comment_lines")
    op.drop_column("symbols", "lines_of_code")
    op.drop_column("symbols", "maintainability_index")
    op.drop_column("symbols", "cyclomatic_complexity")
