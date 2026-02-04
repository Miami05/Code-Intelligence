import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID

from database import Base


class Embedding(Base):
    """Embeddings table - stores vector representations of code symbols."""

    __tablename__ = "embeddings"
    id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: str(uuid.uuid4()))
    symbol_id = Column(
        UUID(as_uuid=True),
        ForeignKey("symbols.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    embedding = Column(Vector(1536), nullable=False)
    model = Column(String(100), nullable=False)
    dimensions = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow())

    def __repr__(self):
        return f"<Embedding(symbol_id={self.symbol_id}, dimensions={self.dimensions})>"
