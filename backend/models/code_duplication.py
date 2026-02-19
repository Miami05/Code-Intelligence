"""Code Duplication Detection Models"""

import uuid
from datetime import datetime

import sqlalchemy
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class CodeDuplication(Base):
    """Stores detected code duplications across files"""

    __tablename__ = "code_duplication"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("repositories.id", ondelete="CASCADE"),
        index=True,
    )
    file1_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("files.id", ondelete="CASCADE"), index=True
    )
    file1_start_line: Mapped[int] = mapped_column(Integer, nullable=False)
    file1_end_line: Mapped[int] = mapped_column(Integer, nullable=False)
    file2_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("files.id", ondelete="CASCADE"), index=True
    )
    file2_start_line: Mapped[int] = mapped_column(Integer, nullable=False)
    file2_end_line: Mapped[int] = mapped_column(Integer, nullable=False)
    similarity_score: Mapped[float] = mapped_column(Float, nullable=False)
    duplicated_lines: Mapped[int] = mapped_column(Integer, nullable=False)
    duplicated_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    code_snippet: Mapped[str] = mapped_column(Text, nullable=True)
    hash_signature: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    repository = relationship("Repository", backref="duplications")
    file1 = relationship(
        "File", foreign_keys=[file1_id], backref="duplications_as_file1"
    )
    file2 = relationship(
        "File", foreign_keys=[file2_id], backref="duplications_as_file2"
    )

    def __repr__(self) -> str:
        return (
            f"<CodeDuplication(id={self.id}, similarity={self.similarity_score:.2f})>"
        )
