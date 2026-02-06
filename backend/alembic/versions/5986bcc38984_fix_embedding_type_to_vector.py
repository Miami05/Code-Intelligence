"""fix_embedding_type_to_vector

Revision ID: 5986bcc38984
Revises: 0e9ce319c94e
Create Date: 2026-02-06 11:35:48.560048

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5986bcc38984"
down_revision: Union[str, None] = "0e9ce319c94e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable vector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Convert embedding column to proper vector type
    op.execute(
        """
        ALTER TABLE embeddings 
        ALTER COLUMN embedding TYPE vector(1536) 
        USING embedding::vector(1536)
    """
    )


def downgrade() -> None:
    op.execute(
        """
        ALTER TABLE embeddings 
        ALTER COLUMN embedding TYPE float[] 
        USING embedding::float[]
    """
    )
