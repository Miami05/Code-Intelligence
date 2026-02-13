"""add source column

Revision ID: 001
Revises: 
Create Date: 2026-02-13 16:24:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create RepoSource enum type
    reposource_enum = sa.Enum('upload', 'github', name='reposource')
    reposource_enum.create(op.get_bind(), checkfirst=True)
    
    # Add source column
    op.add_column('repositories', 
        sa.Column('source', reposource_enum, nullable=False, server_default='upload')
    )
    
    # Update existing GitHub repositories
    op.execute(
        "UPDATE repositories SET source = 'github' WHERE github_url IS NOT NULL"
    )
    
    # Create index
    op.create_index('idx_repositories_source', 'repositories', ['source'])


def downgrade() -> None:
    # Drop index
    op.drop_index('idx_repositories_source', 'repositories')
    
    # Drop column
    op.drop_column('repositories', 'source')
    
    # Drop enum type
    sa.Enum(name='reposource').drop(op.get_bind(), checkfirst=True)
