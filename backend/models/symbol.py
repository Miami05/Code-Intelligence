import enum
import uuid

from sqlalchemy import Column, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID

from database import Base


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
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_id = Column(
        UUID(as_uuid=True),
        ForeignKey("files.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(255), nullable=False, index=True)
    type = Column(SQLEnum(SymbolType), nullable=False, index=True)
    line_start = Column(Integer, nullable=False)
    line_end = Column(Integer)
    signature = Column(Text)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    def __repr__(self) -> str:
        return f"<Symbol(id={self.id}, name={self.name}, type={self.type.value})>"
