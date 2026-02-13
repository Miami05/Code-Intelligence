"""add github fields to repositories

Revision ID: add_github_fields
Revises: add_complexity_001
Create Date: 2026-02-13

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "add_github_fields"
down_revision: Union[str, None] = "add_complexity_001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "repositories", sa.Column("github_url", sa.String(length=500), nullable=True)
    )
    op.add_column(
        "repositories", sa.Column("github_owner", sa.String(length=255), nullable=True)
    )
    op.add_column(
        "repositories", sa.Column("github_repo", sa.String(length=255), nullable=True)
    )
    op.add_column(
        "repositories", sa.Column("github_branch", sa.String(length=100), nullable=True)
    )
    op.add_column(
        "repositories", sa.Column("github_stars", sa.Integer(), nullable=True)
    )
    op.add_column(
        "repositories",
        sa.Column("github_language", sa.String(length=50), nullable=True),
    )

    op.create_index(
        "ix_repositories_github_url", "repositories", ["github_url"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_repositories_github_url", table_name="repositories")
    op.drop_column("repositories", "github_language")
    op.drop_column("repositories", "github_stars")
    op.drop_column("repositories", "github_branch")
    op.drop_column("repositories", "github_repo")
    op.drop_column("repositories", "github_owner")
    op.drop_column("repositories", "github_url")
