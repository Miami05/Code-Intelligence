import enum
import uuid
from typing import Optional

from database import Base
from sqlalchemy import Boolean, Column, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Float, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


class SymbolType(enum.Enum):
    """Types of code symbol we can extract"""

    function = "function"
    class_ = "class"
    variable = "variable"
    procedure = "procedure"
    label = "label"


class Symbol(Base):
    """Symbol table - stores functions, classes, etc."""

    __tablename__ = "symbols"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    file_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("files.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    type = Column(SQLEnum(SymbolType), nullable=False, index=True)
    line_start = Column(Integer, nullable=False)
    line_end = Column(Integer)
    signature: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    cyclomatic_complexity = Column(Integer, nullable=True, index=True)
    maintainability_index = Column(Float, nullable=True)
    lines_of_code = Column(Integer, nullable=True)
    comment_lines = Column(Integer, nullable=True)
    docstring: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    has_docstring: Mapped[bool] = mapped_column(
        Boolean, default=False, index=True, server_default="false"
    )
    docstring_length: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    file = relationship("File", back_populates="symbols")

    __table_args__ = (
        Index("idx_symbols_file_id", "file_id"),
        Index("idx_symbols_name", "name"),
        Index("idx_symbols_type", "type"),
        Index("idx_symbols_file_name", "file_id", "name"),
    )

    def __repr__(self) -> str:
        return f"<Symbol(id={self.id}, name={self.name}, type={self.type.value})>"
