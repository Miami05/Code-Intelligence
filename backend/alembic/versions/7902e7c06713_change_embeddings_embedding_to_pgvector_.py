"""change embeddings.embedding to pgvector and add index

Revision ID: 7902e7c06713
Revises: cc87ed74e223
Create Date: 2026-02-04 17:40:32.395898

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector  # Ensure pgvector is installed

# revision identifiers, used by Alembic.
revision: str = "7902e7c06713"
down_revision: Union[str, None] = "cc87ed74e223"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Enable the vector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # 2. Add the embedding column (assuming 1536 dimensions for OpenAI models)
    # If your model uses a different dimension (e.g. 768 or 384), change 1536 below.
    op.add_column("embeddings", sa.Column("embedding", Vector(1536), nullable=True))

    # 3. Create the HNSW index for faster similarity search
    op.create_index(
        "ix_embeddings_embedding",
        "embeddings",
        ["embedding"],
        unique=False,
        postgresql_using="hnsw",
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )


def downgrade() -> None:
    op.drop_index(
        "ix_embeddings_embedding", table_name="embeddings", postgresql_using="hnsw"
    )
    op.drop_column("embeddings", "embedding")
    op.execute("DROP EXTENSION IF EXISTS vector")
