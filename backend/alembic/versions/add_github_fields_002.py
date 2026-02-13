"""add github fields to repository

Revision ID: add_github_fields_002
Revises: add_complexity_001
Create Date: 2026-02-11
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "add_github_fields_002"
down_revision = "add_complexity_001"
branch_labels = None
depends_on = None


def upgrade():
    # Add source enum
    source_enum = postgresql.ENUM(
        "upload", "github", "gitlab", "bitbucket", name="reposource"
    )
    source_enum.create(op.get_bind(), checkfirst=True)

    # Add new columns
    op.add_column(
        "repositories",
        sa.Column(
            "source",
            sa.Enum("upload", "github", "gitlab", "bitbucket", name="reposource"),
            nullable=False,
            server_default="upload",
        ),
    )
    op.add_column(
        "repositories", sa.Column("github_url", sa.String(500), nullable=True)
    )
    op.add_column(
        "repositories", sa.Column("github_owner", sa.String(255), nullable=True)
    )
    op.add_column(
        "repositories", sa.Column("github_repo", sa.String(255), nullable=True)
    )
    op.add_column(
        "repositories", sa.Column("github_branch", sa.String(255), nullable=True)
    )
    op.add_column(
        "repositories", sa.Column("github_stars", sa.Integer(), nullable=True)
    )
    op.add_column(
        "repositories", sa.Column("github_last_commit", sa.String(255), nullable=True)
    )

    # Create indexes
    op.create_index("idx_repositories_source", "repositories", ["source"])
    op.create_index("idx_repositories_github_owner", "repositories", ["github_owner"])


def downgrade():
    op.drop_index("idx_repositories_github_owner")
    op.drop_index("idx_repositories_source")
    op.drop_column("repositories", "github_last_commit")
    op.drop_column("repositories", "github_stars")
    op.drop_column("repositories", "github_branch")
    op.drop_column("repositories", "github_repo")
    op.drop_column("repositories", "github_owner")
    op.drop_column("repositories", "github_url")
    op.drop_column("repositories", "source")

    # Drop enum
    sa.Enum(name="reposource").drop(op.get_bind(), checkfirst=True)
