"""Add vulnerabilities table

Revision ID: 874d67e7b43c
Revises: 005
Create Date: 2026-02-17 13:36:00.388807+00:00

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "874d67e7b43c"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create vulnerabilities table
    op.create_table(
        "vulnerabilities",
        sa.Column("id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("repository_id", sa.UUID(), nullable=False),
        sa.Column("type", sa.String(length=100), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("cwe_id", sa.String(length=20), nullable=True),
        sa.Column("owasp_category", sa.String(length=100), nullable=True),
        sa.Column("file_path", sa.String(length=1000), nullable=False),
        sa.Column("line_number", sa.Integer(), nullable=False),
        sa.Column("code_snippet", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("recommendation", sa.Text(), nullable=True),
        sa.Column("confidence", sa.String(length=20), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["repository_id"],
            ["repositories.id"],
            name="vulnerabilities_repository_id_fkey",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="vulnerabilities_pkey"),
    )
    
    # Create indexes
    op.create_index(
        "ix_vulnerabilities_repository_id",
        "vulnerabilities",
        ["repository_id"],
        unique=False,
    )
    op.create_index(
        "ix_vulnerabilities_severity",
        "vulnerabilities",
        ["severity"],
        unique=False,
    )
    op.create_index(
        "ix_vulnerabilities_type",
        "vulnerabilities",
        ["type"],
        unique=False,
    )
    op.create_index(
        "ix_vulnerabilities_created_at",
        "vulnerabilities",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    # Drop vulnerabilities table and indexes
    op.drop_index("ix_vulnerabilities_created_at", table_name="vulnerabilities")
    op.drop_index("ix_vulnerabilities_type", table_name="vulnerabilities")
    op.drop_index("ix_vulnerabilities_severity", table_name="vulnerabilities")
    op.drop_index("ix_vulnerabilities_repository_id", table_name="vulnerabilities")
    op.drop_table("vulnerabilities")
